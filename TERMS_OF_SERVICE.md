# Terms of Service

**Cortex Bot** — Last updated: February 2026

By adding Cortex Bot to your Discord server or interacting with it, you agree to these terms.

## What the bot does

Cortex Bot is a session manager and dice roller for Cortex Prime RPG. It tracks campaign state (stress, assets, complications, doom pool, crisis pools, PP, XP) and handles dice pool rolls with automatic calculations. It does not store character sheets.

## Data we collect

The bot stores the following data in its database:

- **Discord server ID and channel ID** to bind campaigns to channels.
- **Discord user IDs and display names** to identify players within a campaign.
- **Campaign state** including stress, assets, complications, trauma, hero dice, doom pool, crisis pools, PP, and XP values.
- **Action log** with inverse data for the undo system. Each logged action references the user who performed it.

No message content is read or stored. No data is shared with third parties. No data is used for analytics, advertising, or training.

## Data retention

Campaign data persists until the GM explicitly ends the campaign via `/campaign end`. When a campaign is ended, all associated data (players, stress, assets, complications, scenes, action log, doom pool, crisis pools) is permanently deleted from the database.

There is no automatic expiration. Inactive campaigns remain stored until manually removed.

## Data access and deletion

Any GM can delete all campaign data at any time using `/campaign end confirm:yes`. There is no separate data export feature. If you need your data removed and cannot access the bot commands, contact the bot operator.

## Availability and warranties

The bot is provided as-is with no guarantees of uptime, availability, or correctness. Session state may be lost due to database errors, hosting issues, or bugs. The bot is not a substitute for keeping your own notes.

## Limitations of liability

The bot operator is not liable for any loss of game data, interrupted sessions, or incorrect dice calculations. Use at your own discretion.

## User responsibilities

- Do not attempt to exploit the bot to disrupt Discord servers or other users.
- Do not use automated tools to spam bot commands.
- The bot respects Discord's Terms of Service. Users must also comply with Discord's terms.

## Changes to these terms

These terms may be updated at any time. Continued use of the bot after changes constitutes acceptance. Significant changes will be noted in the bot's repository.

## Contact

This bot is open source. For questions, issues, or data requests, open an issue at the project repository.
