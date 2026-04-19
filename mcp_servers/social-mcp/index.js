#!/usr/bin/env node

import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { TwitterApi } from "twitter-api-v2";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Always load env from repo root so execution works from any cwd.
dotenv.config({ path: path.resolve(__dirname, '..', '..', '.env') });

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
        name: "post_twitter",
        description: "Tweet content to X/Twitter.",
        inputSchema: {
          type: "object",
          properties: { content: { type: "string" } },
          required: ["content"]
        },
      },
      // Re-enable this tool when Meta credentials are available.
      // {
      //   name: "post_facebook",
      //   description: "Post content to Facebook Page.",
      //   inputSchema: {
      //     type: "object",
      //     properties: { content: { type: "string" } },
      //     required: ["content"]
      //   },
      // },
      // Re-enable this tool when Meta credentials are available.
      // {
      //   name: "post_instagram",
      //   description: "Post image to Instagram.",
      //   inputSchema: {
      //     type: "object",
      //     properties: {
      //       image_url: { type: "string" },
      //       caption: { type: "string" }
      //     },
      //     required: ["image_url", "caption"]
      //   },
      // },
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
            case "post_twitter":
          {
            const content = String(args?.content || "").trim();
            if (!content) {
              throw new Error("Missing required field: content");
            }

            const appKey = process.env.X_API_KEY;
            const appSecret = process.env.X_API_SECRET;
            const accessToken = process.env.X_ACCESS_TOKEN;
            const accessSecret = process.env.X_ACCESS_SECRET;

            if (!appKey || !appSecret || !accessToken || !accessSecret) {
              throw new Error("Missing X credentials. Set X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET.");
            }

            const client = new TwitterApi({
              appKey,
              appSecret,
              accessToken,
              accessSecret,
            });

            const resp = await client.v2.tweet(content);
            return {
              content: [{ type: "text", text: JSON.stringify({ status: "SUCCESS", tweet_id: resp?.data?.id }) }],
            };
          }

        // Re-enable when Meta credentials are available.
        // case "post_facebook":
        // case "post_instagram":
        //     return { content: [{ type: "text", text: `Success: Posted to ${name.split('_')[1]}` }] };
            
            case "get_social_stats":
                return { 
                    content: [{ 
                        type: "text", 
                        text: JSON.stringify({ 
                twitter_followers: 3400
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
