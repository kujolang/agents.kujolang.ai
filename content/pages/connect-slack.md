---
title: "Connect a Kujo agent to Slack"
custom_url: "connect-slack"
description: "Deploy a Kujo Slack bot with its catalog portrait to your Cloudflare account."
social_image: "/assets/images/social/connect-slack.jpg"
template: "connect-slack"
date: 2026-11-20
last_updated: 2026-11-26
nav_hide: true
---

Deploy the agent to your Cloudflare account, give it a name, and connect it to your Slack workspace. The bot gets its catalog portrait automatically.

## Set up your bot

1. Choose **Deploy to Cloudflare**. Sign in to Cloudflare and connect your Git provider. Use the setup key instructions to set `KUJO_SETUP_KEY` and keep it somewhere private.
2. Open your new Worker and follow its guided setup. Choose your bot’s name and use a temporary Slack app configuration token to create it. Slack may require workspace admin permission.
3. Verify the event URL in Slack, then approve the bot’s permissions. Add it to a channel and mention it to get a threaded reply.

## What the Slack bot can do

The bot can help you plan, draft, and review in Slack. It uses Google Gemma 4 through Workers AI. It replies to the person who installed it in one channel. Tool execution and access to other conversations are outside this release.

Your Cloudflare account hosts the bot and supplies the model. Usage counts against your Cloudflare plan’s allowances. [See Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/).
