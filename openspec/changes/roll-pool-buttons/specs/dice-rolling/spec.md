## MODIFIED Requirements

### Requirement: Botao Roll executa rolagem direta

O botao Roll SHALL abrir um pool builder interativo com botoes para montagem incremental do dice pool (conforme spec pool-builder). O botao SHALL NOT usar select menus para composicao de pool.

#### Scenario: Roll via botao abre pool builder

- **WHEN** jogador clica botao "Roll"
- **THEN** bot abre pool builder com botoes de dado, botoes de assets ativos, e controles
- **AND** bot SHALL NOT apresentar select menus para composicao de pool

#### Scenario: Assets disponiveis aparecem como botoes no pool builder

- **WHEN** jogador inicia roll via botao e tem assets ativos
- **THEN** pool builder mostra assets como botoes toggle individuais
