#!/usr/bin/env node

import 'dotenv/config';
import puppeteer from 'puppeteer';
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  {
    name: "browser-mcp",
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
        name: "browse_page",
        description: "Browse a URL and return text content.",
        inputSchema: {
          type: "object",
          properties: { url: { type: "string" } },
          required: ["url"]
        },
      },
      {
        name: "screenshot_page",
        description: "Take a screenshot of a URL.",
        inputSchema: {
          type: "object",
          properties: { 
            url: { type: "string" },
            path: { type: "string" }
          },
          required: ["url"]
        },
      }
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    
    try {
        const browser = await puppeteer.launch({ headless: "new" });
        const page = await browser.newPage();
        
        switch (name) {
            case "browse_page":
                await page.goto(args.url, { waitUntil: 'networkidle0' });
                const content = await page.evaluate(() => document.body.innerText);
                await browser.close();
                return { content: [{ type: "text", text: content.substring(0, 2000) + "..." }] };
            
            case "screenshot_page":
                await page.goto(args.url, { waitUntil: 'networkidle0' });
                const path = args.path || `screenshot_${Date.now()}.png`;
                await page.screenshot({ path: path });
                await browser.close();
                return { content: [{ type: "text", text: `Screenshot saved to ${path}` }] };

            default:
                await browser.close();
                throw new Error(`Tool not found: ${name}`);
        }
    } catch (error) {
         return {
            isError: true,
            content: [{ type: "text", text: `Browser Error: ${error.message}` }],
        };
    }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Browser MCP Server running...");
}

main().catch(console.error);
