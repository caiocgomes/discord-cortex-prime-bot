## MODIFIED Requirements

### Requirement: Help topics use English keys and content

The `/help` command SHALL use English topic keys: `general`, `gm`, `player`, `rolling`. The `@app_commands.choices` SHALL use these English keys as values and English display names. All help text content SHALL be in English. References to other help topics within help text SHALL use the English key names.

#### Scenario: Help topic keys are English

- **WHEN** user types `/help topic:`
- **THEN** autocomplete shows: general, gm, player, rolling
- **AND** SHALL NOT show: geral, jogador, rolagem

#### Scenario: Help general topic in English

- **WHEN** user executes `/help topic:general`
- **THEN** bot responds with general help text in English
- **AND** references to other topics use English names (e.g., "Use /help topic:rolling for dice commands")

#### Scenario: Help rolling topic conditionally mentions doom

- **WHEN** user executes `/help topic:rolling`
- **THEN** help text describes rolling mechanics in English
- **AND** doom pool references use conditional or generic language (since help is not campaign-context-aware)
