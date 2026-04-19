#!/usr/bin/env node

import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { TwitterApi } from 'twitter-api-v2';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Always load env from repo root so execution works from any cwd.
dotenv.config({ path: path.resolve(__dirname, '..', '..', '.env') });

async function main() {
  const content = (process.argv.slice(2).join(' ') || '').trim();
  if (!content) {
    console.error('Missing tweet content');
    process.exit(1);
  }

  if (process.env.DRY_RUN === 'true') {
    console.log(JSON.stringify({ status: 'DRY_RUN_SUCCESS', message: 'Tweet simulated' }));
    return;
  }

  const appKey = process.env.X_API_KEY;
  const appSecret = process.env.X_API_SECRET;
  const accessToken = process.env.X_ACCESS_TOKEN;
  const accessSecret = process.env.X_ACCESS_SECRET;

  if (!appKey || !appSecret || !accessToken || !accessSecret) {
    console.error('Missing X credentials. Set X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET.');
    process.exit(1);
  }

  const client = new TwitterApi({ appKey, appSecret, accessToken, accessSecret });
  const resp = await client.v2.tweet(content);
  console.log(JSON.stringify({ status: 'SUCCESS', tweet_id: resp?.data?.id }));
}

main().catch((err) => {
  console.error(err?.message || String(err));
  process.exit(1);
});
