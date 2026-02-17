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

All output is linear text, no box art, no emoji-only information. The primary user is a blind GM using a screen reader, so every piece of information must be conveyed through text. New interactive features (PP, XP, menu) use buttons instead of selects for screen reader accessibility.

### Views layer (`views/`)

Discord UI components live in `views/`, separate from cogs. This is a substantial subsystem (~1500 lines across 6 files).

**Custom ID convention**: All persistent buttons use `cortex:action_name:param1:param2` format. `make_custom_id()` and `parse_custom_id()` in `views/base.py` handle construction/parsing. Ephemeral buttons append `uuid.uuid4().hex[:8]` to prevent collisions.

**DynamicItem pattern**: Persistent buttons that survive bot restarts extend `discord.ui.DynamicItem[discord.ui.Button]` with a regex `template` attribute and a `from_custom_id()` classmethod. 12 persistent button classes are registered via `bot.add_dynamic_items()` in `views/__init__.py` during `setup_hook()`.

**Post-action view composition**: Every game action responds with a view containing contextual buttons (typically: next action + undo + menu). `MenuButton` appears on all public views for always-available navigation. Key post-action views: `PostRollView`, `PostStressView`, `PostAssetView`, `PostComplicationView`, `PostPPView`, `PostXPView`, `PostDoomActionView`.

**View files**:
- `base.py`: `CortexView` base class (timeout=None), custom ID helpers, `add_die_buttons()`, `add_player_options()`, permission checks
- `common.py`: Shared persistent buttons (`UndoButton`, `CampaignInfoButton`, `MenuButton`) and their post-action views
- `rolling_views.py`: `PoolBuilderView` (interactive pool construction), `PostRollView` with conditional hitch buttons
- `state_views.py`: Action chains for stress/asset/complication/PP/XP. PP uses interactive +1/-1 buttons; XP uses modal input
- `scene_views.py`: Scene start/end lifecycle buttons
- `doom_views.py`: Doom add/remove/roll and crisis pool management

**Startup registration flow**: `bot.setup_hook()` calls `register_persistent_views(bot)` which registers all DynamicItem classes, then loads cogs, then syncs the command tree.

### Hitch handling

When a roll produces hitches, `PostRollView` shows `HitchComplicationButton` and `HitchDoomButton`. Die size scales with hitch count: 1→d6, 2→d8, 3→d10, 4→d12 (RAW p.17). Complications check for existing ones on the target player and step up if found. Doom button adds `hitch_count` d6s to the doom pool. Exactly 1 PP is awarded per hitch resolution regardless of count.

### Menu system

`/menu` command and `MenuButton` (persistent, on all views) show a contextual action panel. With an active scene: Roll, Stress, Asset, Complication, PP, XP, Undo, CampaignInfo, and Doom (if enabled). Without a scene: SceneStart and CampaignInfo.

### Configuration

`config.py` uses Pydantic settings with `CORTEX_BOT_` env prefix. Variables: `CORTEX_BOT_TOKEN` (SecretStr), `CORTEX_BOT_DB`. Loads from `.env` file.

## Testing

Tests use `pytest-asyncio` with `asyncio_mode = "auto"` (set in `pyproject.toml`). Each test file creates an in-memory SQLite DB via `tmp_path` fixture. No Discord mocking needed for service/model tests since those layers are decoupled from Discord.

The existing test suite covers: dice validation, roller mechanics, state manager operations (assets, stress, complications, PP, undo), and a full game flow integration test.

## Cortex Prime rules reference

`cortex-prime-rules-extraction.md` at the repo root contains the complete mechanical extraction from the handbook. Consult it for rules questions about stress mechanics, hitches, botch, heroic success thresholds, effect dice, and step up/down semantics.
