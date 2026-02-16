# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Discord bot for Cortex Prime RPG. Session state manager + assisted dice roller. Replaces the abandoned CortexPal2000. No character sheets stored in the bot; players bring their own traits and compose dice pools at roll time.

## Commands

```bash
# Install dependencies
uv sync --dev

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_dice.py

# Run a single test class or method
uv run pytest tests/test_state_manager.py::TestStress::test_add_new_stress

# Run with verbose output
uv run pytest -v

# Run the bot (requires CORTEX_BOT_TOKEN env var)
uv run python -m cortex_bot.bot
```

## Architecture

The bot follows a lifecycle of **Campaign -> Scene -> Roll**. A campaign is bound to a Discord channel (one per channel). Scenes are ephemeral containers that scope assets, complications, and crisis pools. Rolls compose dice pools from player-provided notation plus optional assets.

### Layer separation

- **Cogs** (`cogs/`) handle Discord interaction plumbing: parameter parsing, permission checks (GM vs player), autocomplete, and response formatting. They instantiate `StateManager` per-command rather than holding persistent state.
- **Services** (`services/`) contain pure game logic. `roller.py` is stateless (roll, hitches, botch, best options). `state_manager.py` mutates DB state and logs every action with inverse data for undo. `formatter.py` produces screen-reader-friendly linear text output.
- **Models** (`models/`) hold the DB schema and queries (`database.py`) plus dice validation/step mechanics (`dice.py`).

### Database pattern

`Database.connect()` is an `@asynccontextmanager`. Use it directly with `async with`, never await it first:

```python
async with self.db.connect() as conn:  # correct
    ...
```

### Permission system

Two levels of GM-like access exist:

- **GM** (`is_gm=1`): Full control. Only the GM can `delegate`, `undelegate`, and `campaign_end`. These commands use `is_gm_check()` in `cogs/campaign.py` which checks `is_gm` directly.
- **Delegate** (`is_delegate=1`): A player promoted by the GM who can execute GM-only commands (stress/doom/scene/undo) while keeping their own player state (stress, assets, PP, XP). Bridge scene step-down applies to delegates as normal players.

New GM-only commands **must** use `has_gm_permission()` from `cortex_bot.utils`, not `actor["is_gm"]` directly. The only exceptions are `campaign_end`, `delegate`, and `undelegate` which remain strictly GM-only.

The `/gmroll` command lets GM/delegates roll dice without injecting personal state (no assets, stress, complications, or PP spending).

### Undo system

Every state mutation logs an `action_log` entry with `inverse_data` describing how to reverse it. The undo cog fetches the last undone=0 action and calls `StateManager.execute_undo(inverse_data)` which performs the reverse operation (delete/insert/update). GM and delegates can undo any action; players can only undo their own.

### Configurable modules

Campaign `config` JSON toggles optional features: `doom_pool`, `hero_dice`, `trauma`, `best_mode`. Cogs check these flags before exposing functionality.

### Accessibility

All output is linear text, no box art, no emoji-only information. The primary user is a blind GM using a screen reader, so every piece of information must be conveyed through text.

## Testing

Tests use `pytest-asyncio` with `asyncio_mode = "auto"` (set in `pyproject.toml`). Each test file creates an in-memory SQLite DB via `tmp_path` fixture. No Discord mocking needed for service/model tests since those layers are decoupled from Discord.

The existing test suite covers: dice validation, roller mechanics, state manager operations (assets, stress, complications, PP, undo), and a full game flow integration test.

## Cortex Prime rules reference

`cortex-prime-rules-extraction.md` at the repo root contains the complete mechanical extraction from the handbook. Consult it for rules questions about stress mechanics, hitches, botch, heroic success thresholds, effect dice, and step up/down semantics.
