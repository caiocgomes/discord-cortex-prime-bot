## Context

The bot has ~25 source files and ~337 tests. Every user-facing string is currently inline in the file that sends it, with no centralized string registry. The primary user is a blind GM using a screen reader, so output structure directly affects usability. The codebase already separates concerns cleanly: formatter functions produce text, cogs handle Discord plumbing, views handle UI components.

The current `format_campaign_info()` receives structured data (campaign dict, players list, player_states dict, scene, doom_pool) but has no access to campaign config, so it can't know which modules are active. Similarly, `format_roll_result()` has no way to know whether doom_pool is enabled, so it always mentions it in hitch messages.

## Goals / Non-Goals

**Goals:**

- Every user-facing string in English with consistent formatting conventions (UPPERCASE headers, blank-line separation, explicit empty states).
- `format_campaign_info()` renders module status so players can discover what's enabled.
- Hitch messages only reference Doom Pool when it's actually enabled.
- Error messages tell the user what to do next, not just what went wrong.
- Tests updated in lockstep so the suite never breaks mid-change.

**Non-Goals:**

- No i18n framework or centralized strings file. The codebase is small enough that inline strings are fine, and adding a translation layer would be over-engineering for a single-language bot.
- No changes to game logic, database schema, or command signatures (except the two new optional params on formatter functions).
- No changes to Discord command names. `/campaign setup` stays `/campaign setup`. Only the `description=` kwarg and response text change.
- Not touching the `confirm:sim` choice value in `campaign_end`. Changing it would break muscle memory for the existing GM. Only the surrounding text changes.

## Decisions

### 1. Strings stay inline, one constant extracted

Every file keeps its own strings. The only exception is the "No active campaign" error, which appears in 8+ locations with minor wording variations. That goes to `utils.py` as `NO_CAMPAIGN_MSG = "No active campaign in this channel. Use /campaign setup to create one."` and callers reference it directly.

Alternative considered: a centralized `strings.py` mapping keys to text. Rejected because the bot isn't multilingual, the strings are tightly coupled to their context (error messages include guidance specific to the command), and a centralized file would make reading any single cog harder without meaningful payoff.

### 2. New formatter signatures are additive (optional params with defaults)

`format_campaign_info()` gains `config: dict | None = None`. When None, the MODULES section is omitted. This keeps backward compatibility for any call site that doesn't have config handy, though in practice all callers (campaign.py info, common.py CampaignInfoButton, scene.py _info) do have it.

`format_roll_result()` gains `doom_enabled: bool = False`. Default False means existing callers that don't pass it get the doom-free hitch message, which is the safe default (don't advertise what doesn't exist).

Alternative considered: passing the full config dict to format_roll_result. Rejected because the function only needs one bit of information and shouldn't know about the config schema.

### 3. Campaign info output structure uses line-per-category, not inline joining

Current output joins everything into a single line per player: `"Alice (GM): Stress Physical d8. Assets: Sword d8 (scene). PP 3, XP 0."` This is hard to scan for sighted users and produces a wall of text for screen readers.

New structure puts the player name on its own line (UPPERCASE), then each state category on a separate line with a label prefix. Empty categories explicitly show "none". This produces more lines but each line is semantically distinct, which is what screen readers need.

```
ALICE (GM)
Stress: Physical d8
Assets: Sword d8 (scene)
Complications: none
PP 3, XP 0
```

The `---` separator between players is replaced by blank lines, which are the universal section break for both sighted and screen reader users.

### 4. Help topic keys rename from PT-BR to English

`geral/gm/jogador/rolagem` become `general/gm/player/rolling`. The `HELP_TOPICS` dict keys, the `@app_commands.choices` values, and the `/help topic:X` references in help text all update together. This is a breaking change for anyone who memorized `/help topic:jogador`, but the slash command autocomplete will guide them.

### 5. Phase ordering: formatter first, then self-contained modules, then views, then cogs

The formatter is the foundation. Most tests assert on formatter output strings. Changing it first and updating `test_formatter.py` in the same step means the test suite stays green after phase 1.

Undo and help are self-contained (own file, own tests, no cross-dependencies on string content). Views depend on formatter through `format_action_confirm` and `format_roll_result` calls. Cogs depend on both formatter and views. Supporting files (utils, base) can go at any point.

Ordered phases:
1. Formatter core + test_formatter.py
2. Undo system + test_undo_feedback.py
3. Help system + test_help.py
4. Views + test_views.py
5. Cogs (campaign, scene, state, rolling, doom, menu)
6. Supporting files (base.py, utils.py)
7. Remaining tests (test_guided_messages, test_integration, test_delegation)
8. Verification grep + full test run

### 6. Doom roll output in views vs cogs uses the same pattern

Both `DoomRollButton.callback` (in views/doom_views.py) and `DoomCog._doom_roll` (in cogs/doom.py) format doom roll output inline with nearly identical code. This change translates both but does not refactor them into a shared function. The duplication is minor (10 lines), and merging them would require passing the view instance into the cog or extracting a service function for something that's pure formatting. Not worth the coupling for this change.

## Risks / Trade-offs

**337 tests touching string assertions across 7 test files** - The biggest risk is missing a string update in a test and having it fail silently or getting a false green (test still passes because the assertion was too loose). Mitigation: run `uv run pytest` after each phase, and finish with a grep for remaining Portuguese words across src/ and tests/.

**Discord command descriptions require bot restart + tree.sync()** - Changing `description=` kwargs won't take effect until the bot restarts and syncs the command tree. This is expected behavior, not a risk, but worth noting for deployment: the change is not hot-reloadable for command descriptions.

**Help topic key rename is a user-visible breaking change** - Anyone who memorized `/help topic:jogador` will get an error. Mitigation: Discord autocomplete will show the new options. The user base is small (one play group), so this is acceptable.

**`confirm:sim` choice value stays Portuguese** - Changing it to `confirm:yes` would break the GM's muscle memory and requires updating the check in `campaign_end`. Not worth it for this change. The surrounding text explains what to do in English.
