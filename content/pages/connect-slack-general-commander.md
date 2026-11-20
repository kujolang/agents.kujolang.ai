---
title: "Connect General Commander to Slack"
custom_url: "connect-slack-general-commander"
description: "Install General Commander as a distinct Slack bot with the local Kujo setup assistant."
social_image: "/assets/images/social/connect-slack-general-commander.jpg"
date: 2026-11-20
last_updated: 2026-11-20
nav_hide: true
---

The self-hosted preview installs General Commander as a distinct Slack bot.
You need permission to create an app in your Slack workspace, Node.js 24 or
later, and the [Kujo Agents checkout](https://github.com/kujolang/kujo-agents).

## Start the setup assistant

[Download the versioned setup package](/assets/downloads/kujo-slack-setup-0.1.0.tgz),
then run this command with the downloaded file and your Kujo Agents checkout:

```sh
npm exec --package=./kujo-slack-setup-0.1.0.tgz -- kujo-slack-setup "$HOME/.local/state/kujo/slack" /path/to/kujo-agents
```

[Open the local setup assistant](http://127.0.0.1:4396/setup?agent=chain.general-commander)

## Install and verify

The assistant opens Slack with a prefilled app manifest. Approve the installation,
invite the bot to a test channel, and enter the Slack app credentials in the
local assistant. Socket Mode connects directly to Slack. The website does not
collect credentials. The assistant shows the test mention and confirms delivery
after Commander replies in its own thread.

For text advisory replies, supply an existing Software Factory checkout as the
third argument after configuring its ChatGPT sign-in. Each request remains
staged until an operator approves the model reply in the local assistant.
Production workflows retain their own controls.
