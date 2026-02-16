# Cortex Prime Discord Bot

Session state manager and assisted dice roller for Cortex Prime RPG on Discord. Replaces the abandoned CortexPal2000.

The bot manages the campaign lifecycle (campaigns, scenes, assets, stress, complications, doom pool) and provides assisted rolling with automatic hitch detection, botch, best-mode options, and heroic success evaluation. No character sheets are stored; players bring their own traits and compose dice pools at roll time.

Designed with accessibility as a priority: all output is linear text, compatible with screen readers.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
git clone https://github.com/caiocgomes/discord-cortex-prime-bot.git
cd discord-cortex-prime-bot
uv sync
```

Copy the example environment file and fill in your bot token:

```bash
cp .env.example .env
```

Edit `.env` and set `CORTEX_BOT_TOKEN` to your Discord bot token.

## Running

```bash
uv run python -m cortex_bot.bot
```

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `CORTEX_BOT_TOKEN` | Yes | - | Discord bot token |
| `CORTEX_BOT_DB` | No | `cortex_bot.db` | Path to SQLite database file |

Variables can be set via environment or `.env` file in the project root.

## Testing

```bash
uv run pytest
```

## Deploy with systemd

The repository includes a `cortex-bot.service` unit file for running as a systemd service.

1. Create a dedicated user:
   ```bash
   sudo useradd -r -s /usr/sbin/nologin cortex-bot
   ```

2. Clone the repository to `/opt/cortex-bot` and install dependencies:
   ```bash
   sudo git clone https://github.com/caiocgomes/discord-cortex-prime-bot.git /opt/cortex-bot
   cd /opt/cortex-bot
   sudo -u cortex-bot uv sync
   ```

3. Create the environment file:
   ```bash
   sudo mkdir -p /etc/cortex-bot
   sudo cp .env.example /etc/cortex-bot/env
   sudo chmod 600 /etc/cortex-bot/env
   ```
   Edit `/etc/cortex-bot/env` and set `CORTEX_BOT_TOKEN`.

4. Install and start the service:
   ```bash
   sudo cp cortex-bot.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now cortex-bot
   ```

5. Check status:
   ```bash
   sudo systemctl status cortex-bot
   sudo journalctl -u cortex-bot -f
   ```

## License

MIT. See [LICENSE](LICENSE).
