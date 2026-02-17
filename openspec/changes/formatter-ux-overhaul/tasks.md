## 1. Supporting constants

- [x] 1.1 Add `NO_CAMPAIGN_MSG` constant to `src/cortex_bot/utils.py`

## 2. Formatter core + tests

- [x] 2.1 Rewrite `format_roll_result()` in `formatter.py`: English strings, add `doom_enabled: bool = False` parameter, conditional hitch message (doom mentioned only when enabled), multiple hitches scale complication die in message
- [x] 2.2 Rewrite `format_campaign_info()` in `formatter.py`: English strings, UPPERCASE headers, per-player multi-line blocks with explicit "none" for empty categories, add `config: dict | None = None` parameter, MODULES section, conditional DOOM POOL section
- [x] 2.3 Rewrite `format_scene_end()` in `formatter.py`: English strings, UPPERCASE headers, "Next:" guidance line
- [x] 2.4 Rewrite `format_action_confirm()` in `formatter.py`: English strings, "{Entity} {action}. {Details}." pattern
- [x] 2.5 Update all tests in `tests/test_formatter.py` to match new English output and new signatures (config, doom_enabled)

## 3. Undo system + tests

- [x] 3.1 Translate all ACTION_LABELS templates in `src/cortex_bot/cogs/undo.py` to English
- [x] 3.2 Translate undo command description and response messages in `undo.py`
- [x] 3.3 Update `tests/test_undo_feedback.py` to match English strings

## 4. Help system + tests

- [x] 4.1 Rename help topic keys from PT-BR to English (`geral`→`general`, `jogador`→`player`, `rolagem`→`rolling`) in `src/cortex_bot/cogs/help.py`
- [x] 4.2 Rewrite all 4 help text blocks (HELP_GENERAL, HELP_GM, HELP_PLAYER, HELP_ROLLING) in English
- [x] 4.3 Update `@app_commands.choices` with English display names and values
- [x] 4.4 Update `tests/test_help.py` to match English keys and content

## 5. Views

- [x] 5.1 Translate `src/cortex_bot/views/base.py`: 3 shared error strings to English
- [x] 5.2 Translate `src/cortex_bot/views/rolling_views.py`: pool builder status, button labels ("Roll"/"Clear"/"Remove last"), hitch button labels ("Complication d6"), ComplicationNameModal title, all callback messages
- [x] 5.3 Translate `src/cortex_bot/views/state_views.py`: ~28 strings across stress/asset/complication/PP/XP chains, button labels ("Scene Asset"/"Scene Complication")
- [x] 5.4 Translate `src/cortex_bot/views/doom_views.py`: doom add/remove/roll callback messages, "empty"/"added"/"removed" strings
- [x] 5.5 Translate `src/cortex_bot/views/common.py`: undo/campaign info/menu callback messages
- [x] 5.6 Translate `src/cortex_bot/views/scene_views.py`: scene start callback and guide text
- [x] 5.7 Update `tests/test_views.py` to match all English strings
- [x] 5.8 Update `tests/test_guided_messages.py` to match English strings

## 6. Cogs

- [x] 6.1 Translate `src/cortex_bot/cogs/campaign.py`: command descriptions, setup/info/delegate/undelegate/campaign_end messages, error messages with guidance. Pass `config` to `format_campaign_info()`. Replace no-campaign errors with `NO_CAMPAIGN_MSG`.
- [x] 6.2 Translate `src/cortex_bot/cogs/scene.py`: command descriptions, start/end/info messages. Replace no-campaign errors with `NO_CAMPAIGN_MSG`.
- [x] 6.3 Translate `src/cortex_bot/cogs/state.py`: command descriptions, ~75 inline strings, `_player_label` returns "You" instead of "Voce", error messages with guidance. Replace no-campaign errors with `NO_CAMPAIGN_MSG`.
- [x] 6.4 Translate `src/cortex_bot/cogs/rolling.py`: command descriptions, roll/gmroll messages, error messages with guidance. Pass `doom_enabled` to `format_roll_result()`. Replace no-campaign errors with `NO_CAMPAIGN_MSG`.
- [x] 6.5 Translate `src/cortex_bot/cogs/doom.py`: command descriptions, doom/crisis messages. Replace no-campaign errors with `NO_CAMPAIGN_MSG`.
- [x] 6.6 Translate `src/cortex_bot/cogs/menu.py`: command description, menu text, cooldown message. Replace no-campaign error with `NO_CAMPAIGN_MSG`.

## 7. Remaining tests

- [x] 7.1 Update `tests/test_integration.py` string assertions to English
- [x] 7.2 Update `tests/test_delegation.py` if any PT-BR string assertions exist
- [x] 7.3 Update `tests/test_state_manager.py` if any PT-BR string assertions exist

## 8. Verification

- [x] 8.1 Run `uv run pytest` and confirm all tests pass
- [x] 8.2 Grep for remaining Portuguese words across `src/` and `tests/` (rolou, tirou, campanha, cena, jogador, apenas, nenhum, voce, criado, removid, encerrada, desfeit, vazio) and fix any remaining occurrences
