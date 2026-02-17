# Privacy Policy

**Cortex Bot** — Last updated: February 2026

This policy describes what data Cortex Bot collects, how it is used, and how it can be deleted.

## Data collected

Cortex Bot stores only the data necessary to manage Cortex Prime RPG sessions. Specifically:

| Data | Purpose | Source |
|---|---|---|
| Discord server ID | Bind campaign to a server | Discord API |
| Discord channel ID | Bind campaign to a channel | Discord API |
| Discord user ID | Identify players across sessions | Discord API |
| Display name | Show player names in campaign info | Discord API |
| Campaign configuration | Track enabled modules (doom pool, hero dice, trauma, best mode) | GM input via `/campaign setup` |
| Game state | Stress, assets, complications, trauma, hero dice, PP, XP, doom pool, crisis pools, scenes | Player and GM actions during play |
| Action log | Enable undo functionality | Automatically generated per state change |

## Data not collected

- Message content is never read or stored.
- Voice data is never accessed.
- No data is collected from users who do not interact with the bot.
- No cookies, tracking pixels, or analytics of any kind.

## How data is used

All stored data is used exclusively to run the RPG session. Nothing is shared with third parties, sold, used for advertising, or used for model training.

## Where data is stored

Data is stored in a SQLite database on the server hosting the bot. No data is replicated to external services or cloud storage beyond the hosting environment.

## Data retention

Campaign data exists until the GM runs `/campaign end confirm:yes`, which permanently deletes the campaign and all associated records (players, stress, assets, complications, scenes, action log, doom pool, crisis pools). There is no automatic expiration for inactive campaigns.

## Data deletion

- **Full campaign deletion**: The GM can delete all campaign data at any time with `/campaign end confirm:yes`.
- **Individual action reversal**: The `/undo` command reverses the last logged action and its stored data.
- **Manual requests**: If you cannot access bot commands, contact the bot operator to request data removal.

## Children's privacy

The bot does not knowingly collect data from users under 13. Discord's own Terms of Service require users to be at least 13 years old.

## Changes to this policy

This policy may be updated at any time. Changes will be reflected in this file with an updated date. Continued use of the bot after changes constitutes acceptance.

## Contact

For privacy questions or data deletion requests, open an issue at the project repository.
