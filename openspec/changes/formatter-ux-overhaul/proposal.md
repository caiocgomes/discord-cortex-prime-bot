## Why

Three problems compound into one: the bot lies about what's available, hides what's configured, and forces the primary user (a blind GM on a screen reader) to parse inconsistent bilingual output.

First, hitch messages and help text reference "Doom Pool" unconditionally. When doom_pool is disabled in campaign config, players see options that don't exist. The GM gets asked about it, wastes time explaining it's off. Second, `/campaign info` doesn't show which modules are active. The GM has to remember what was set during `/campaign setup`, and there's no way for players to discover it. Third, all user-facing text is mixed Portuguese and English with no visual hierarchy. Sighted users can't scan it; screen readers parse it as a flat wall of text with no structural cues.

These aren't cosmetic. They produce wrong decisions (acting on phantom doom pool), missing information (module state invisible), and accessibility friction (no headers, no blank-line separation, silent omission of empty states).

## What Changes

- Translate every user-facing string to English. Game terms (hitch, botch, step up, stressed out, taken out, effect die) stay as-is since they're Cortex Prime vocabulary.
- Restructure formatter output with UPPERCASE section headers, blank-line separation between sections, and explicit empty states ("none" instead of silent omission).
- Add `config` parameter to `format_campaign_info()` to render a MODULES section showing each module's active/inactive status.
- Add `doom_enabled` parameter to `format_roll_result()` so hitch messages only mention Doom Pool when it's actually on.
- Standardize error messages to the pattern "{What went wrong}. {What to do next.}" across all cogs and views.
- Standardize confirmation messages to "{Entity} {action}. {Details}." pattern.
- Extract the shared "No active campaign" error to a constant in `utils.py` (it appears in 8+ locations with minor variations).
- Translate all help text, undo feedback templates, command descriptions, modal titles, and button labels.

## Capabilities

### Modified Capabilities
- `campaign-info`: Restructured output with UPPERCASE headers, per-player blocks (name on its own line, each state category on separate lines with explicit "none"), SCENE ELEMENTS section, DOOM POOL section, and new MODULES section showing doom_pool/hero_dice/trauma/best_mode as active or inactive. Signature gains `config: dict | None = None`.
- `dice-rolling`: `format_roll_result()` gains `doom_enabled: bool = False`. Hitch message becomes conditional: mentions Doom Pool only when enabled. All Portuguese strings replaced.
- `scene-lifecycle`: Scene start/end messages in English with guidance text. Scene end gains "Next:" line pointing to `/scene start` and `/campaign info`.
- `undo-system`: All 30+ ACTION_LABELS templates translated to English. Undo command responses in English.
- `help-system`: All 4 help blocks rewritten in English. Topic keys change from `geral/gm/jogador/rolagem` to `general/gm/player/rolling`. Choice names updated accordingly.
- `state-tracking`: All ~75 inline strings in state cog translated. Error messages gain guidance. `_player_label` returns "You" instead of "Voce".
- `doom-pool`: All doom/crisis messages in English. "vazio" becomes "empty".
- `action-menu`: Menu text in English. Cooldown message in English.
- `interactive-views`: All view strings (pool builder status, hitch buttons, select prompts, modal titles/labels, PP/XP feedback) translated. `ComplicationNameModal` title becomes "Complication name". Button labels like "Complicacao d6" become "Complication d6", "Rolar" becomes "Roll", "Limpar" becomes "Clear", "Remover ultimo" becomes "Remove last".

## Impact

- `src/cortex_bot/services/formatter.py`: Rewrite all 4 functions. New signature params on format_campaign_info (config) and format_roll_result (doom_enabled). New output structure with UPPERCASE headers.
- `src/cortex_bot/utils.py`: Add `NO_CAMPAIGN_MSG` constant.
- `src/cortex_bot/cogs/undo.py`: Translate ACTION_LABELS dict and command description/responses.
- `src/cortex_bot/cogs/help.py`: Rewrite all 4 help blocks, rename topic keys, update Choice names.
- `src/cortex_bot/cogs/campaign.py`: Translate setup/info/delegate/undelegate/campaign_end messages and command descriptions. Pass config to format_campaign_info.
- `src/cortex_bot/cogs/scene.py`: Translate start/end/info messages and command descriptions.
- `src/cortex_bot/cogs/state.py`: Translate ~75 strings across asset/stress/trauma/complication/PP/XP/hero groups and command descriptions.
- `src/cortex_bot/cogs/rolling.py`: Translate roll/gmroll messages and command descriptions. Pass doom_enabled to format_roll_result.
- `src/cortex_bot/cogs/doom.py`: Translate doom/crisis messages and command descriptions.
- `src/cortex_bot/cogs/menu.py`: Translate menu text and cooldown message.
- `src/cortex_bot/views/rolling_views.py`: Translate pool builder, hitch buttons, modal, callbacks.
- `src/cortex_bot/views/state_views.py`: Translate ~28 strings across state chains.
- `src/cortex_bot/views/doom_views.py`: Translate doom add/remove/roll callbacks.
- `src/cortex_bot/views/common.py`: Translate undo/campaign info/menu callbacks.
- `src/cortex_bot/views/scene_views.py`: Translate scene start callback.
- `src/cortex_bot/views/base.py`: Translate 3 shared error strings.
- `tests/test_formatter.py`: Update all 44 tests.
- `tests/test_undo_feedback.py`: Update 11 tests.
- `tests/test_help.py`: Update 9 tests.
- `tests/test_views.py`: Update ~20 assertions referencing PT-BR strings.
- `tests/test_guided_messages.py`: Update 9 tests.
- `tests/test_integration.py`: Update 2 assertions.
- `tests/test_delegation.py`: Check for PT-BR assertions.
