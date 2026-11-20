---
title: "Connect a Kujo Agent to Slack"
custom_url: "connect-slack"
description: "Install a named Kujo bot with its catalog portrait in your Slack workspace."
social_image: "/assets/images/social/connect-slack.jpg"
template: "connect-slack"
date: 2026-11-20
last_updated: 2026-11-20
nav_hide: true
---

Set up a named Slack bot for the agent you selected. You need Node.js 24 or later, a [Kujo Agents checkout](https://github.com/kujolang/kujo-agents), and permission to create an app in the Slack workspace.

## 1. Start the local setup assistant

[Download the setup package](/assets/downloads/kujo-slack-setup-0.1.1.tgz). Run the command below from your download folder. Replace `/path/to/kujo-agents` with your checkout path.

## 2. Install the bot and upload its portrait

Open the local setup assistant and follow its prefilled Slack manifest. In Slack’s **Basic Information → Display Information**, upload the PNG from this page as the app icon and save changes. Approve the app’s installation, invite the bot to your test channel, and enter its credentials in the local assistant. Slack handles app consent. The website never receives the credentials.

## 3. Verify the first reply

Send the test mention shown in the assistant and wait for your bot’s reply in the same thread. This verifies the Slack connection without using a model.

For text advice, add your Software Factory checkout as the third positional argument and configure its model sign-in. General Commander uses ChatGPT. Other profiles use the configured Hermes free model. Every advisory request requires local approval. Profile-specific tools, Factory execution and native approvals require their own authorized host.

For another bot, use its own state directory and a different `--port`. Open the loopback address printed by the assistant.
