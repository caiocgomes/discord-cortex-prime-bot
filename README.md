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

The repository includes an install script that handles everything: creates the service user, clones the repo, installs dependencies, configures systemd, and sets permissions.

```bash
curl -sSL https://raw.githubusercontent.com/caiocgomes/discord-cortex-prime-bot/main/install.sh | sudo bash
```

Or, if the repo is already cloned:

```bash
sudo bash install.sh
```

The script will prompt you to configure `CORTEX_BOT_TOKEN` in `/etc/cortex-bot/env` if it hasn't been set.

To update an existing installation, run the script again. It pulls the latest code and restarts the service.

To check status:

```bash
sudo systemctl status cortex-bot
sudo journalctl -u cortex-bot -f
```

## License

MIT. See [LICENSE](LICENSE).
