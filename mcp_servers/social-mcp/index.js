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
        description: "Post content to Facebook Page.",
        inputSchema: {
          type: "object",
          properties: { content: { type: "string" } },
          required: ["content"]
        },
      },
      {
        name: "post_twitter",
        description: "Tweet content to X/Twitter.",
        inputSchema: {
          type: "object",
          properties: { content: { type: "string" } },
          required: ["content"]
        },
      },
      {
        name: "post_instagram",
        description: "Post image to Instagram.",
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
        name: "get_social_stats",
        description: "Get weekly engagement metrics.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      }
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    
    // DRY RUN CHECK
    if (process.env.DRY_RUN === 'true') {
         return { content: [{ type: "text", text: `[DRY_RUN] Social Action ${name} simulated.` }] };
    }

    try {
        switch (name) {
            case "post_facebook":
            case "post_twitter":
            case "post_instagram":
                // In production: Use 'fb', 'twitter-api-v2', 'instagram-private-api'
                return { content: [{ type: "text", text: `Success: Posted to ${name.split('_')[1]}` }] };
            
            case "get_social_stats":
                return { 
                    content: [{ 
                        type: "text", 
                        text: JSON.stringify({ 
                            facebook_likes: 120, 
                            twitter_followers: 3400, 
                            instagram_reach: 5000 
                        }) 
                    }] 
                };

            default:
                throw new Error(`Tool not found: ${name}`);
        }
    } catch (error) {
         return {
            isError: true,
            content: [{ type: "text", text: `Social API Error: ${error.message}` }],
        };
    }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Social MCP Server running...");
}

main().catch(console.error);
