#!/usr/bin/env node

import 'dotenv/config';
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

import { emailActions } from './actions/email.js';
import { linkedinActions } from './actions/linkedin.js';
import { calendarActions } from './actions/calendar.js';

const server = new Server(
  {
    name: "autonomous-fte-mcp",
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
        name: "send_email",
        description: "Send a formal email to a recipient.",
        inputSchema: {
          type: "object",
          properties: {
            to: { type: "string", format: "email" },
            subject: { type: "string" },
            body: { type: "string" },
          },
          required: ["to", "subject", "body"],
        },
      },
      {
        name: "draft_email",
        description: "Draft an email for review.",
        inputSchema: {
          type: "object",
          properties: {
            to: { type: "string" },
            subject: { type: "string" },
            body: { type: "string" },
          },
          required: ["to", "subject", "body"],
        },
      },
      {
        name: "linkedin_post",
        description: "Post a message to LinkedIn.",
        inputSchema: {
          type: "object",
          properties: {
            text: { type: "string", description: "The content of the post" },
            media: { type: "string", description: "URL to image/video (optional)" },
          },
          required: ["text"],
        },
      },
      {
        name: "calendar_event",
        description: "Schedule an event in the calendar.",
        inputSchema: {
          type: "object",
          properties: {
            title: { type: "string" },
            start: { type: "string", description: "ISO timestamp" },
            end: { type: "string", description: "ISO timestamp" },
            location: { type: "string" },
          },
          required: ["title", "start", "end"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "send_email":
        return { content: [{ type: "text", text: JSON.stringify(await emailActions.send_email(args)) }] };
      case "draft_email":
        return { content: [{ type: "text", text: JSON.stringify(await emailActions.draft_email(args)) }] };
      case "linkedin_post":
        return { content: [{ type: "text", text: JSON.stringify(await linkedinActions.linkedin_post(args)) }] };
      case "calendar_event":
        return { content: [{ type: "text", text: JSON.stringify(await calendarActions.calendar_event(args)) }] };
      default:
        throw new Error(`Tool not found: ${name}`);
    }
  } catch (error) {
    return {
      isError: true,
      content: [{ type: "text", text: error.message }],
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Autonomous FTE MCP Server (Action Layer) running...");
}

main().catch(console.error);
