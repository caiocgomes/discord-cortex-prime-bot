## MODIFIED Requirements

### Requirement: Identificar hitches e botches

O bot SHALL identificar dados que rolaram 1 (hitches) e reportar no resultado. Se todos os dados rolarem 1, SHALL identificar como botch. Hitches SHALL ser excluídos das sugestões de total e effect die. `format_roll_result()` SHALL accept an optional `doom_enabled: bool = False` parameter. When hitches are present and doom_enabled is True, the hitch message SHALL mention the Doom Pool as an option. When doom_enabled is False, the hitch message SHALL NOT mention the Doom Pool.

#### Scenario: Hitch with doom enabled

- **WHEN** result contains d8:1 among other dice
- **AND** doom_enabled is True
- **THEN** bot reports hitch and message includes: "GM may award 1 PP and create a d6 complication, or add a die to the Doom Pool."

#### Scenario: Hitch with doom disabled

- **WHEN** result contains d8:1 among other dice
- **AND** doom_enabled is False
- **THEN** bot reports hitch and message includes: "GM may award 1 PP and create a d6 complication."
- **AND** message SHALL NOT mention Doom Pool

#### Scenario: Botch

- **WHEN** all dice roll 1
- **THEN** bot reports "Botch" with total zero, regardless of doom_enabled setting

#### Scenario: Multiple hitches scale complication die

- **WHEN** result contains multiple dice that rolled 1
- **THEN** hitch message SHALL indicate the scaled complication die size (1 hitch = d6, 2 = d8, 3 = d10, 4+ = d12)
