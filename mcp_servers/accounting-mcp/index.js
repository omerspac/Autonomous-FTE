#!/usr/bin/env node

import 'dotenv/config';
import xmlrpc from 'xmlrpc';
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const ODOO_URL = process.env.ODOO_URL || 'http://localhost';
const ODOO_PORT = process.env.ODOO_PORT || 8069;
const ODOO_DB = process.env.ODOO_DB || 'odoo';
const ODOO_USER = process.env.ODOO_USER || 'admin';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || 'admin';

const common = xmlrpc.createClient({ host: ODOO_URL, port: ODOO_PORT, path: '/xmlrpc/2/common' });
const models = xmlrpc.createClient({ host: ODOO_URL, port: ODOO_PORT, path: '/xmlrpc/2/object' });

let uid = null;

// Authenticate
async function authenticate() {
    return new Promise((resolve, reject) => {
        common.methodCall('authenticate', [ODOO_DB, ODOO_USER, ODOO_PASSWORD, {}], (error, value) => {
            if (error) reject(error);
            else resolve(value);
        });
    });
}

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

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_financial_summary",
        description: "Get financial summary from Odoo (Invoices, Revenue).",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "create_invoice",
        description: "Create a customer invoice.",
        inputSchema: {
          type: "object",
          properties: {
            partner_name: { type: "string" },
            amount: { type: "number" },
            description: { type: "string" }
          },
          required: ["partner_name", "amount", "description"]
        },
      }
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    
    if (process.env.DRY_RUN === 'true') {
        return { content: [{ type: "text", text: `[DRY_RUN] Executed ${name} with args: ${JSON.stringify(args)}` }] };
    }

    try {
        if (!uid) uid = await authenticate();
        
        switch (name) {
            case "get_financial_summary":
                // Mocking complex Odoo query for demonstration logic
                // In production: Use 'execute_kw' to search_read 'account.move'
                return { 
                    content: [{ 
                        type: "text", 
                        text: JSON.stringify({ 
                            revenue_ytd: 15000, 
                            pending_invoices: 3, 
                            cash_balance: 5000 
                        }) 
                    }] 
                };

            case "create_invoice":
                // Mocking create logic
                // In production: 'execute_kw' to create 'account.move'
                return { 
                    content: [{ 
                        type: "text", 
                        text: `Invoice created for ${args.partner_name} amount ${args.amount}` 
                    }] 
                };
            default:
                throw new Error(`Tool not found: ${name}`);
        }
    } catch (error) {
        return {
            isError: true,
            content: [{ type: "text", text: `Odoo Error: ${error.message}` }],
        };
    }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Accounting MCP Server running...");
}

main().catch(console.error);
