## MODIFIED Requirements

### Requirement: Botao Roll executa rolagem direta

O botao Roll SHALL abrir um pool builder interativo com conteudo diferenciado por papel. Para jogadores, o pool builder SHALL mostrar botoes de dado (d4-d12) e assets do jogador como toggles. Para GM/delegates, o pool builder SHALL mostrar botoes de dado (d4-d12) e stress + complications de todos os jogadores + complications de cena como toggles. Cada toggle SHALL incluir o nome do dono no label.

#### Scenario: Jogador abre pool builder com seus assets

- **WHEN** jogador comum clica botao "Roll"
- **THEN** pool builder mostra botoes de dado (d4-d12) e assets do jogador como toggles
- **AND** labels dos assets seguem formato "NomeAsset dX"

#### Scenario: GM abre pool builder com stress e complications de todos

- **WHEN** GM clica botao "Roll"
- **THEN** pool builder mostra botoes de dado (d4-d12) e toggles com stress e complications de todos os jogadores + complications de cena
- **AND** labels seguem formato "NomeJogador: TipoStress dX" ou "NomeJogador: NomeComp dX"
- **AND** complications de cena usam "Cena: NomeComp dX"

#### Scenario: GM sem jogadores com stress ou complications

- **WHEN** GM clica "Roll" e nenhum jogador tem stress ou complications
- **THEN** pool builder mostra apenas botoes de dado e controles, sem row de toggles

#### Scenario: Delegate abre pool builder como GM

- **WHEN** delegate clica botao "Roll"
- **THEN** pool builder mostra visao de GM (stress/complications de todos)
- **AND** SHALL NOT mostrar assets do delegate
