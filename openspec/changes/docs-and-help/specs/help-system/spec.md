## ADDED Requirements

### Requirement: Comando /help com topicos por papel

O sistema SHALL fornecer um comando `/help` com parametro opcional `topic` do tipo Choice. Os valores de topic SHALL ser: geral (default), gm, jogador, rolagem. Quando invocado sem topic, SHALL exibir a variante "geral". O conteudo de cada variante SHALL ser hardcoded no cog como strings, sem dependencia de arquivos externos.

#### Scenario: Help geral (default)

- **WHEN** usuario executa `/help` sem parametro topic
- **THEN** bot exibe visao geral do lifecycle (setup -> scene -> roll), lista de grupos de comandos com uma frase descritiva cada, e dica de que `/help topic:gm` ou `/help topic:jogador` da mais detalhes.

#### Scenario: Help GM

- **WHEN** usuario executa `/help topic:gm`
- **THEN** bot exibe comandos organizados por momento: setup (`/campaign setup`), durante cena (`/stress add`, `/complication add`, `/doom`), entre cenas (`/scene start`, `/scene end`), administracao (`/campaign end`, `/delegate`, `/undo`). SHALL incluir pelo menos um exemplo de uso por momento.

#### Scenario: Help jogador

- **WHEN** usuario executa `/help topic:jogador`
- **THEN** bot exibe apenas comandos relevantes para jogador: `/roll` (com explicacao de include e extra), `/asset`, `/pp`, `/complication`, `/campaign info`. SHALL omitir todos os comandos GM-only.

#### Scenario: Help rolagem

- **WHEN** usuario executa `/help topic:rolagem`
- **THEN** bot exibe referencia completa de notacao de dados (1d8, 2d10), include de assets, extra com PP, dificuldade, hitches, botch, best mode, effect die. SHALL ser suficiente para um jogador novo entender como montar e interpretar uma rolagem.

#### Scenario: Acessibilidade do output

- **WHEN** bot exibe qualquer variante de help
- **THEN** output SHALL ser texto linear, sem tabelas, sem formatacao visual complexa, legivel por screen reader.

### Requirement: Mensagem guiada pos-setup

O sistema SHALL exibir uma mensagem de proximos passos ao final do output de `/campaign setup` bem-sucedido. A mensagem SHALL orientar sobre os comandos imediatos disponiveis.

#### Scenario: Onboarding apos setup

- **WHEN** GM executa `/campaign setup` com sucesso
- **THEN** bot exibe o output normal de confirmacao seguido de bloco "Proximos passos" com: `/scene start` para iniciar cena, `/roll` para rolar dados, `/campaign info` para ver estado, `/help` para referencia de comandos.

#### Scenario: Setup falha nao exibe onboarding

- **WHEN** `/campaign setup` falha (canal ja tem campanha, sem jogadores, etc.)
- **THEN** bot exibe apenas a mensagem de erro, sem bloco de proximos passos.

### Requirement: Mensagem guiada pos-scene start

O sistema SHALL exibir uma mensagem de comandos de jogo ao final do output de `/scene start` bem-sucedido.

#### Scenario: Orientacao apos iniciar cena

- **WHEN** GM executa `/scene start` com sucesso
- **THEN** bot exibe o output normal seguido de bloco com comandos de jogo: `/roll` para rolar, `/asset add` para criar assets, `/campaign info` para ver estado. Para GM: `/stress add`, `/complication add`, `/doom` (se habilitado).

### Requirement: Mensagem guiada pos-scene end

O sistema SHALL exibir uma mensagem de continuidade ao final do output de `/scene end`.

#### Scenario: Orientacao apos encerrar cena

- **WHEN** GM executa `/scene end` com sucesso
- **THEN** bot exibe o output detalhado de fim de cena (step downs, remocoes) seguido de bloco com: `/scene start` para iniciar nova cena, `/campaign info` para ver estado persistente.
