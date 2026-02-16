## MODIFIED Requirements

### Requirement: Select menu chains para comandos multi-parametro

Comandos que exigem multiplos parametros (stress add, complication add, asset add) SHALL usar sequencia de botoes e/ou selects dinamicos para coletar cada parametro. Selecao de dado (d4-d12) SHALL usar 5 botoes individuais em 1 ActionRow. Selecao de jogador SHALL usar botoes quando <= 5 jogadores, ou select quando > 5. Selecao de tipo de stress SHALL usar botoes (maximo 4 tipos). Listas longas (nomes de assets/complications comuns) SHALL manter select. Cada etapa intermediaria SHALL ser efemera.

#### Scenario: Chain de stress add completa com botoes

- **WHEN** GM clica botao "Stress Add"
- **AND** campanha tem 4 jogadores (excluindo GM)
- **THEN** bot apresenta 4 botoes com nomes dos jogadores (1 por botao)
- **WHEN** GM clica botao do jogador
- **THEN** bot apresenta botoes com tipos de stress da campanha (ex: Physical, Mental)
- **WHEN** GM clica botao do tipo
- **THEN** bot apresenta 5 botoes de dado: d4, d6, d8, d10, d12
- **WHEN** GM clica botao do dado
- **THEN** bot executa stress add e exibe resultado com botoes contextuais

#### Scenario: Chain de stress add com > 5 jogadores usa select

- **WHEN** GM clica botao "Stress Add"
- **AND** campanha tem 7 jogadores (excluindo GM)
- **THEN** bot apresenta select menu com 7 jogadores como opcoes
- **WHEN** GM seleciona jogador
- **THEN** chain continua com botoes para tipo e dado

#### Scenario: Chain de asset add completa

- **WHEN** GM clica botao "Asset Add"
- **THEN** bot apresenta botoes de jogadores (ou select se > 5) mais botao "Asset de Cena"
- **WHEN** GM seleciona jogador ou cena
- **THEN** bot apresenta select menu com nomes de assets comuns pre-definidos
- **WHEN** GM seleciona nome
- **THEN** bot apresenta 5 botoes de dado: d4, d6, d8, d10, d12
- **WHEN** GM seleciona dado
- **THEN** bot executa asset add e exibe resultado com botoes contextuais

#### Scenario: Chain de complication add completa

- **WHEN** GM clica botao "Complication Add"
- **THEN** bot apresenta botoes de jogadores (ou select se > 5) mais botao "Complicacao de Cena"
- **WHEN** GM seleciona alvo
- **THEN** bot apresenta select com nomes de complication comuns
- **WHEN** GM seleciona nome
- **THEN** bot apresenta 5 botoes de dado: d4, d6, d8, d10, d12
- **WHEN** GM seleciona dado
- **THEN** bot executa complication add e exibe resultado com botoes contextuais

#### Scenario: Mensagens intermediarias sao efemeras

- **WHEN** bot envia botoes ou select intermediario durante uma chain
- **THEN** mensagem SHALL ser efemera (visivel apenas para quem clicou)

### Requirement: Doom pool via botoes

Botoes de doom (add, remove, roll) SHALL estar disponiveis apenas quando o modulo doom_pool esta habilitado na campanha. Doom add via botao SHALL apresentar 5 botoes de dado (d4-d12) em vez de select. Doom remove SHALL apresentar botoes com dados presentes no pool (deduplicados por tamanho). Doom roll SHALL executar diretamente.

#### Scenario: Doom add via botao

- **WHEN** GM clica botao "Doom Add"
- **THEN** bot apresenta 5 botoes de dado: d4, d6, d8, d10, d12
- **WHEN** GM clica botao de dado
- **THEN** bot adiciona ao doom pool e exibe resultado com botoes de doom

#### Scenario: Doom remove via botao

- **WHEN** GM clica botao "Doom Remove"
- **AND** doom pool contem d6, d8, d8
- **THEN** bot apresenta botoes: d6, d8 (deduplicados por tamanho)
- **WHEN** GM clica d8
- **THEN** bot remove um d8 do pool e exibe resultado

#### Scenario: Botoes de doom nao aparecem sem modulo

- **WHEN** campanha nao tem doom_pool habilitado
- **THEN** nenhuma resposta SHALL incluir botoes relacionados a doom
