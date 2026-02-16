## MODIFIED Requirements

### Requirement: Gerenciar assets

O sistema SHALL suportar operacoes de add, step up, step down e remove em assets. Assets SHALL ter nome, die size (d4-d12), dono (jogador ou cena), e duracao (cena ou sessao). Jogadores SHALL gerenciar seus proprios assets; GM SHALL gerenciar qualquer asset.

#### Scenario: Adicionar asset para si mesmo

- **WHEN** Alice executa `/asset add name:"Improvised Torch" die:d6`
- **THEN** asset "Improvised Torch" d6 e criado para Alice com duracao "cena".

#### Scenario: Adicionar asset de sessao

- **WHEN** Alice executa `/asset add name:"Magic Ring" die:d8 duration:session`
- **THEN** asset "Magic Ring" d8 e criado para Alice com duracao "sessao" (persiste entre cenas).

#### Scenario: Step up de asset

- **WHEN** Alice executa `/asset stepup name:"Improvised Torch"`
- **THEN** asset passa de d6 para d8.

#### Scenario: Step up alem de d12

- **WHEN** usuario tenta step up de asset que ja e d12
- **THEN** bot informa que d12 e o maximo.

#### Scenario: Step down de asset d4

- **WHEN** usuario tenta step down de asset d4
- **THEN** asset e eliminado (step down de d4 remove o dado).

#### Scenario: GM cria asset de cena (sem dono)

- **WHEN** GM executa `/asset add name:"Slippery Floor" die:d8 scene_asset:yes`
- **THEN** asset de cena "Slippery Floor" d8 e criado sem dono especifico.

#### Scenario: Description do parametro player

- **WHEN** usuario visualiza a description do parametro `player` em `/asset add`
- **THEN** description SHALL ser "Jogador dono do asset (default: voce)" sem mencao a "asset de cena".
