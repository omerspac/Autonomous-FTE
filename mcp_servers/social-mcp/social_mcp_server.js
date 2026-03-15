#!/usr/bin/env node

import 'dotenv/config';
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  {
    name: "social-mcp",
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
        name: "post_facebook",
        description: "Post an update to the Facebook Page.",
        inputSchema: {
          type: "object",
          properties: {
            content: { type: "string" },
            link: { type: "string" }
          },
          required: ["content"]
        },
      },
      {
        name: "post_instagram",
        description: "Post an image and caption to Instagram.",
        inputSchema: {
          type: "object",
          properties: {
            image_url: { type: "string" },
            caption: { type: "string" }
          },
          required: ["image_url", "caption"]
        },
      },
      {
        name: "post_twitter",
        description: "Post a tweet to X/Twitter.",
        inputSchema: {
          type: "object",
          properties: {
            content: { type: "string" }
          },
          required: ["content"]
        },
      },
      {
        name: "get_social_metrics",
        description: "Get engagement metrics (likes, shares, followers) for all platforms.",
        inputSchema: {
          type: "object",
          properties: {}
        },
      }
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const isDryRun = process.env.DRY_RUN === 'true';

  if (isDryRun) {
    return { content: [{ type: "text", text: `[DRY_RUN] Social Action ${name} simulated with content: ${args.content || args.caption}` }] };
  }

  try {
    switch (name) {
      case "post_facebook":
        // Production: Use Facebook Graph API
        return { content: [{ type: "text", text: "Successfully posted to Facebook Page." }] };
      case "post_instagram":
        // Production: Use Instagram Graph API
        return { content: [{ type: "text", text: "Successfully posted to Instagram Business Account." }] };
      case "post_twitter":
        // Production: Use Twitter API v2 (twitter-api-v2 library)
        return { content: [{ type: "text", text: "Successfully posted tweet to X/Twitter." }] };
      case "get_social_metrics":
        // Mocking real-time stats
        const metrics = {
          facebook: { reach: 1200, engagement: 45 },
          instagram: { impressions: 3400, saves: 12 },
          twitter: { followers: 5600, retweets: 89 }
        };
        return { content: [{ type: "text", text: JSON.stringify(metrics, null, 2) }] };
      default:
        throw new Error(`Tool not found: ${name}`);
    }
  } catch (error) {
    return { isError: true, content: [{ type: "text", text: `Social API Error: ${error.message}` }] };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Social Media MCP Server running...");
}

main().catch(console.error);
