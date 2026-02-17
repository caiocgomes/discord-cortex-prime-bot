## ADDED Requirements

### Requirement: All user-facing strings in English

Every user-facing string in the bot SHALL be in English. This includes: command descriptions, response messages, error messages, confirmation messages, button labels, modal titles, select menu placeholders, help text, undo feedback templates, and formatter output. Game terms from Cortex Prime vocabulary (hitch, botch, step up, stressed out, taken out, effect die) SHALL remain as-is since they are English game terminology.

#### Scenario: Command descriptions in English

- **WHEN** user views slash command descriptions in Discord
- **THEN** all descriptions SHALL be in English (e.g., "Roll dice in Cortex Prime" not "Rolar dados no Cortex Prime")

#### Scenario: Button labels in English

- **WHEN** bot presents interactive buttons
- **THEN** labels SHALL be in English (e.g., "Roll" not "Rolar", "Clear" not "Limpar", "Remove last" not "Remover ultimo", "Complication d6" not "Complicacao d6")

#### Scenario: Modal titles in English

- **WHEN** bot presents a modal dialog
- **THEN** title SHALL be in English (e.g., "Complication name" not "Nome da complicacao")

#### Scenario: Self-reference uses "You"

- **WHEN** a player performs an action on themselves
- **THEN** feedback SHALL use "You" not "Voce" (e.g., "You: 2 to 3 PP (+1)")

### Requirement: Error messages include guidance

Every error message SHALL follow the pattern "{What went wrong}. {What to do next.}" The guidance part SHALL tell the user a concrete action to resolve the situation.

#### Scenario: No active campaign error

- **WHEN** user executes a command in a channel without a campaign
- **THEN** bot responds: "No active campaign in this channel. Use /campaign setup to create one."

#### Scenario: Not registered error

- **WHEN** unregistered user tries to roll
- **THEN** bot responds: "You are not registered in this campaign. Ask the GM to add you via /campaign setup."

#### Scenario: Assets not found error

- **WHEN** user includes asset names that don't exist
- **THEN** bot responds: "Assets not found: {names}. Check the names and try again."

#### Scenario: Insufficient PP error

- **WHEN** user tries to spend PP they don't have
- **THEN** bot responds: "Not enough PP. You have {current}, need {required}."

### Requirement: Shared NO_CAMPAIGN_MSG constant

The "No active campaign" error message SHALL be defined once as `NO_CAMPAIGN_MSG` in `utils.py` and referenced by all callers. The constant value SHALL be "No active campaign in this channel. Use /campaign setup to create one."

#### Scenario: All no-campaign errors use the constant

- **WHEN** any command encounters no active campaign
- **THEN** the response text SHALL match `NO_CAMPAIGN_MSG` exactly

### Requirement: Formatter output uses UPPERCASE section headers

All section headers in formatter output SHALL be UPPERCASE (e.g., "CAMPAIGN:", "PLAYERS", "SCENE ELEMENTS", "DOOM POOL", "MODULES"). Sections SHALL be separated by blank lines. This applies to `format_campaign_info()`, `format_scene_end()`, and `format_roll_result()`.

#### Scenario: Campaign info sections use UPPERCASE

- **WHEN** user views campaign info
- **THEN** output uses UPPERCASE headers: "CAMPAIGN:", "PLAYERS" (implicit via player name blocks), "SCENE ELEMENTS", "DOOM POOL", "MODULES"
- **AND** sections are separated by blank lines

#### Scenario: Scene end uses UPPERCASE

- **WHEN** scene ends with removed assets
- **THEN** output uses UPPERCASE header "SCENE ENDED:" and "REMOVED (scene scope)"
- **AND** includes "Next:" guidance line pointing to `/scene start` and `/campaign info`

### Requirement: Empty states are always explicit

When a state category has no entries, the output SHALL show "none" or "empty" explicitly instead of silently omitting the category. This applies to stress, assets, complications in player blocks, and to the doom pool when enabled but empty.

#### Scenario: Player with no stress shows "none"

- **WHEN** player has no stress entries
- **THEN** campaign info shows "Stress: none" for that player

#### Scenario: Player with no assets shows "none"

- **WHEN** player has no assets
- **THEN** campaign info shows "Assets: none" for that player

#### Scenario: Empty doom pool shows "empty"

- **WHEN** doom_pool is enabled but contains no dice
- **THEN** campaign info shows "DOOM POOL\nempty"
