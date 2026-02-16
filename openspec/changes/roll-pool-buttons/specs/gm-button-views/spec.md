## MODIFIED Requirements

### Requirement: Select menu chains para comandos multi-parâmetro

Comandos que exigem múltiplos parâmetros (stress add, complication add, asset add) SHALL usar sequência de botões e/ou selects dinâmicos para coletar cada parâmetro. Seleção de dado (d4-d12) SHALL usar 5 botões individuais em 1 ActionRow. Seleção de jogador SHALL usar botões quando <= 5 jogadores, ou select quando > 5. Seleção de tipo de stress SHALL usar botões (máximo 4 tipos). Listas longas (nomes de assets/complications comuns) SHALL manter select. Cada etapa intermediária SHALL ser efêmera.

#### Scenario: Chain de stress add completa com botões

- **WHEN** GM clica botão "Stress Add"
- **AND** campanha tem 4 jogadores (excluindo GM)
- **THEN** bot apresenta 4 botões com nomes dos jogadores (1 por botão)
- **WHEN** GM clica botão do jogador
- **THEN** bot apresenta botões com tipos de stress da campanha (ex: Physical, Mental)
- **WHEN** GM clica botão do tipo
- **THEN** bot apresenta 5 botões de dado: d4, d6, d8, d10, d12
- **WHEN** GM clica botão do dado
- **THEN** bot executa stress add e exibe resultado com botões contextuais

#### Scenario: Chain de stress add com > 5 jogadores usa select

- **WHEN** GM clica botão "Stress Add"
- **AND** campanha tem 7 jogadores (excluindo GM)
- **THEN** bot apresenta select menu com 7 jogadores como opções
- **WHEN** GM seleciona jogador
- **THEN** chain continua com botões para tipo e dado

#### Scenario: Chain de asset add completa

- **WHEN** GM clica botão "Asset Add"
- **THEN** bot apresenta botões de jogadores (ou select se > 5) mais botão "Asset de Cena"
- **WHEN** GM seleciona jogador ou cena
- **THEN** bot apresenta select menu com nomes de assets comuns pré-definidos
- **WHEN** GM seleciona nome
- **THEN** bot apresenta 5 botões de dado: d4, d6, d8, d10, d12
- **WHEN** GM seleciona dado
- **THEN** bot executa asset add e exibe resultado com botões contextuais

#### Scenario: Chain de complication add completa

- **WHEN** GM clica botão "Complication Add"
- **THEN** bot apresenta botões de jogadores (ou select se > 5) mais botão "Complicacao de Cena"
- **WHEN** GM seleciona alvo
- **THEN** bot apresenta select com nomes de complication comuns
- **WHEN** GM seleciona nome
- **THEN** bot apresenta 5 botões de dado: d4, d6, d8, d10, d12
- **WHEN** GM seleciona dado
- **THEN** bot executa complication add e exibe resultado com botões contextuais

#### Scenario: Mensagens intermediárias são efêmeras

- **WHEN** bot envia botões ou select intermediário durante uma chain
- **THEN** mensagem SHALL ser efêmera (visível apenas para quem clicou)

### Requirement: Botão Roll executa rolagem direta

O botão Roll SHALL abrir um modal com TextInput para montagem do dice pool (conforme spec dice-pool-modal). O botão SHALL NOT usar select menus para composição de pool.

#### Scenario: Roll via botão abre modal

- **WHEN** jogador clica botão "Roll"
- **THEN** bot abre modal com campos TextInput para dados e assets
- **AND** bot SHALL NOT apresentar select menus para composição de pool

#### Scenario: Assets disponíveis aparecem no placeholder do modal

- **WHEN** jogador inicia roll via botão e tem assets ativos
- **THEN** modal mostra assets disponíveis no placeholder do campo de assets

### Requirement: Doom pool via botões

Botões de doom (add, remove, roll) SHALL estar disponíveis apenas quando o módulo doom_pool está habilitado na campanha. Doom add via botão SHALL apresentar 5 botões de dado (d4-d12) em vez de select. Doom remove SHALL apresentar botões com dados presentes no pool (deduplicados por tamanho). Doom roll SHALL executar diretamente.

#### Scenario: Doom add via botão

- **WHEN** GM clica botão "Doom Add"
- **THEN** bot apresenta 5 botões de dado: d4, d6, d8, d10, d12
- **WHEN** GM clica botão de dado
- **THEN** bot adiciona ao doom pool e exibe resultado com botões de doom

#### Scenario: Doom remove via botão

- **WHEN** GM clica botão "Doom Remove"
- **AND** doom pool contém d6, d8, d8
- **THEN** bot apresenta botões: d6, d8 (deduplicados por tamanho)
- **WHEN** GM clica d8
- **THEN** bot remove um d8 do pool e exibe resultado

#### Scenario: Botões de doom não aparecem sem módulo

- **WHEN** campanha não tem doom_pool habilitado
- **THEN** nenhuma resposta SHALL incluir botões relacionados a doom
