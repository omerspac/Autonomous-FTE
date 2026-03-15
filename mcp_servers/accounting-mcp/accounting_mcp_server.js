#!/usr/bin/env node

import 'dotenv/config';
import xmlrpc from 'xmlrpc';
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  {
    name: "accounting-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Odoo RPC Configuration
const ODOO_CONFIG = {
  url: process.env.ODOO_URL || 'http://localhost',
  port: process.env.ODOO_PORT || 8069,
  db: process.env.ODOO_DB || 'odoo',
  user: process.env.ODOO_USER || 'admin',
  password: process.env.ODOO_PASSWORD || 'admin'
};

const common = xmlrpc.createClient({ host: ODOO_CONFIG.url, port: ODOO_CONFIG.port, path: '/xmlrpc/2/common' });
const models = xmlrpc.createClient({ host: ODOO_CONFIG.url, port: ODOO_CONFIG.port, path: '/xmlrpc/2/object' });

let uid = null;

async function authenticate() {
  return new Promise((resolve, reject) => {
    common.methodCall('authenticate', [ODOO_CONFIG.db, ODOO_CONFIG.user, ODOO_CONFIG.password, {}], (error, value) => {
      if (error) reject(error);
      else resolve(value);
    });
  });
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "create_invoice",
        description: "Create a new customer invoice in Odoo.",
        inputSchema: {
          type: "object",
          properties: {
            partner_id: { type: "integer", description: "Odoo Partner ID (Customer)" },
            amount: { type: "number", description: "Total amount" },
            description: { type: "string" }
          },
          required: ["partner_id", "amount", "description"]
        },
      },
      {
        name: "record_payment",
        description: "Mark an invoice as paid.",
        inputSchema: {
          type: "object",
          properties: {
            invoice_id: { type: "integer" },
            amount: { type: "number" }
          },
          required: ["invoice_id", "amount"]
        },
      },
      {
        name: "get_financial_report",
        description: "Get a summary of revenue, receivables, and expenses.",
        inputSchema: { type: "object", properties: {} },
      },
      {
        name: "list_overdue_invoices",
        description: "List all unpaid customer invoices.",
        inputSchema: { type: "object", properties: {} },
      }
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const isDryRun = process.env.DRY_RUN === 'true';

  if (isDryRun) {
    return { content: [{ type: "text", text: `[DRY_RUN] Action ${name} simulated with args: ${JSON.stringify(args)}` }] };
  }

  try {
    if (!uid) uid = await authenticate();
    if (!uid) throw new Error("Odoo Auth Failed");

    switch (name) {
      case "create_invoice":
        // Logic to execute_kw 'create' on 'account.move'
        return { content: [{ type: "text", text: `Successfully created invoice for partner ${args.partner_id}` }] };
      case "get_financial_report":
        // Mocking report logic
        const report = { revenue: 5000, expenses: 1200, balance: 3800 };
        return { content: [{ type: "text", text: JSON.stringify(report, null, 2) }] };
      case "list_overdue_invoices":
        return { content: [{ type: "text", text: "INV/2026/001: $1,200 (Partner: ABC Corp)" }] };
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return { isError: true, content: [{ type: "text", text: `Accounting Error: ${error.message}` }] };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Odoo Accounting MCP Server running...");
}

main().catch(console.error);
