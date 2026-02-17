## ADDED Requirements

### Requirement: Campaign info displays module configuration

`format_campaign_info()` SHALL accept an optional `config: dict | None = None` parameter. When config is provided, the output SHALL include a MODULES section listing each configurable module (doom_pool, hero_dice, trauma, best_mode) with its status as "active" or "inactive". When config is None, the MODULES section SHALL be omitted.

#### Scenario: Campaign info with all modules active

- **WHEN** campaign has config `{"doom_pool": true, "hero_dice": true, "trauma": true, "best_mode": true}`
- **AND** user requests campaign info
- **THEN** output includes MODULES section showing all four modules as "active"

#### Scenario: Campaign info with mixed module config

- **WHEN** campaign has config `{"doom_pool": true, "hero_dice": false, "trauma": false, "best_mode": true}`
- **THEN** output includes:
  ```
  MODULES
  doom_pool: active
  hero_dice: inactive
  trauma: inactive
  best_mode: active
  ```

#### Scenario: Campaign info without config parameter

- **WHEN** `format_campaign_info()` is called with config=None
- **THEN** output SHALL NOT include a MODULES section

### Requirement: Campaign info uses structured per-player blocks

Each player in campaign info output SHALL be rendered as a multi-line block: player name in UPPERCASE on its own line (with role suffix if GM or delegate), followed by each state category on a separate line with a label prefix. Empty categories SHALL explicitly show "none". Players SHALL be separated by blank lines.

#### Scenario: Player with all state categories populated

- **WHEN** Alice is GM with Stress Physical d8, Asset Sword d8 (scene), Complication Wounded d6, PP 3, XP 1
- **THEN** output renders:
  ```
  ALICE (GM)
  Stress: Physical d8
  Assets: Sword d8 (scene)
  Complications: Wounded d6
  PP 3, XP 1
  ```

#### Scenario: Player with no state

- **WHEN** Bob has no stress, no assets, no complications, PP 1, XP 0
- **THEN** output renders:
  ```
  BOB
  Stress: none
  Assets: none
  Complications: none
  PP 1, XP 0
  ```

#### Scenario: Campaign header with active scene

- **WHEN** campaign "Dark Fantasy" has active scene "Tavern Fight"
- **THEN** output starts with:
  ```
  CAMPAIGN: Dark Fantasy
  Active scene: Tavern Fight
  ```

#### Scenario: Campaign header without active scene

- **WHEN** campaign "Dark Fantasy" has no active scene
- **THEN** output starts with:
  ```
  CAMPAIGN: Dark Fantasy
  Active scene: none
  ```

### Requirement: Campaign info renders doom pool conditionally

The DOOM POOL section in campaign info SHALL only appear when doom_pool is enabled in campaign config. When the doom pool exists but is empty, it SHALL show "empty" explicitly.

#### Scenario: Doom pool with dice

- **WHEN** doom_pool is enabled and contains d6, d8
- **THEN** output includes:
  ```
  DOOM POOL
  d6, d8
  ```

#### Scenario: Doom pool enabled but empty

- **WHEN** doom_pool is enabled and contains no dice
- **THEN** output includes:
  ```
  DOOM POOL
  empty
  ```

#### Scenario: Doom pool disabled

- **WHEN** doom_pool is disabled in campaign config
- **THEN** output SHALL NOT include a DOOM POOL section
