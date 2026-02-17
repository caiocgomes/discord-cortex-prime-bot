## MODIFIED Requirements

### Requirement: Botões contextuais em toda resposta do bot

Toda resposta de sucesso do bot SHALL incluir uma View com botões representando as ações mais prováveis como próximo passo, determinadas pelo contexto da ação que acabou de ser executada. Respostas de erro SHALL NOT incluir botões.

#### Scenario: Botões após rolagem

- **WHEN** jogador ou GM executa roll ou gmroll com sucesso
- **THEN** resposta inclui botões: Roll, Undo
- **AND** se a rolagem produziu hitches, inclui botões: Criar complicação, +Doom (se doom habilitado)
- **AND** se doom_pool habilitado, inclui botão Doom Roll
- **AND** inclui botão Menu

#### Scenario: Botões após scene start

- **WHEN** GM executa scene start com sucesso
- **THEN** resposta inclui botões: Roll, Stress Add, Asset Add, Complication Add, Menu
- **AND** se doom_pool habilitado, inclui botão Doom Add

#### Scenario: Botões após scene end

- **WHEN** GM encerra uma cena com sucesso
- **THEN** resposta inclui botões: Scene Start, Campaign Info, Menu

#### Scenario: Botões após ação de state (stress/asset/complication)

- **WHEN** GM executa stress add, asset add, ou complication add com sucesso
- **THEN** resposta inclui botão Undo, botão para repetir a mesma categoria de ação, e botão Menu

#### Scenario: Botões após campaign setup

- **WHEN** GM cria campanha com sucesso
- **THEN** resposta inclui botão Scene Start e botão Menu

#### Scenario: Botões após campaign/scene info

- **WHEN** usuário consulta campaign info ou scene info
- **THEN** se há cena ativa, resposta inclui botão Roll e botão Menu
- **AND** se não há cena ativa, resposta inclui botão Scene Start e botão Menu

#### Scenario: Sem botões em respostas de erro

- **WHEN** bot envia mensagem de erro (campanha não encontrada, permissão negada, etc.)
- **THEN** resposta SHALL NOT incluir View com botões

### Requirement: Doom pool via botoes

Botoes de doom (add, remove, roll) SHALL estar disponiveis apenas quando o modulo doom_pool esta habilitado na campanha. Doom add via botao SHALL apresentar 5 botoes de dado (d4-d12) em vez de select. Doom remove SHALL apresentar botoes com dados presentes no pool (deduplicados por tamanho). Doom roll SHALL executar diretamente. Doom Roll SHALL estar disponivel tambem na PostRollView quando doom_pool esta habilitado, permitindo o GM rolar oposicao diretamente apos uma rolagem de jogador.

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

#### Scenario: Doom Roll na PostRollView

- **WHEN** doom_pool habilitado e jogador executa roll com sucesso
- **THEN** PostRollView inclui botao "Doom Roll"
- **WHEN** GM clica "Doom Roll"
- **THEN** bot rola todo o doom pool e exibe resultado com best options e sugestao de dificuldade

#### Scenario: Botoes de doom nao aparecem sem modulo

- **WHEN** campanha nao tem doom_pool habilitado
- **THEN** nenhuma resposta SHALL incluir botoes relacionados a doom
