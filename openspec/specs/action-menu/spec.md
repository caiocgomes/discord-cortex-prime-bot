## Requirements

### Requirement: Comando /menu apresenta painel de acoes

O bot SHALL oferecer um comando `/menu` que envia mensagem publica com botoes de acao baseados no contexto atual da campanha. O jogador/GM pode fixar esta mensagem para acesso rapido.

#### Scenario: Menu com cena ativa

- **WHEN** GM executa /menu e campanha tem cena ativa
- **THEN** bot envia mensagem publica com botoes: Roll, Stress Add, Asset Add, Complication Add, PP, XP, Undo, Campaign Info
- **AND** se doom_pool habilitado, inclui botoes Doom Add, Doom Remove, Doom Roll

#### Scenario: Menu sem cena ativa

- **WHEN** GM executa /menu e campanha nao tem cena ativa
- **THEN** bot envia mensagem com botoes: Scene Start, Campaign Info

#### Scenario: Menu sem campanha

- **WHEN** usuario executa /menu em canal sem campanha
- **THEN** bot responde com mensagem efemera informando que nao ha campanha

### Requirement: Cooldown de 10 segundos no /menu

O comando /menu SHALL ter cooldown de 10 segundos por usuario para evitar spam de paineis.

#### Scenario: Cooldown ativo

- **WHEN** usuario executa /menu dentro de 10 segundos apos ultimo uso
- **THEN** bot responde com mensagem efemera informando cooldown restante

#### Scenario: Cooldown expirado

- **WHEN** usuario executa /menu apos 10 segundos do ultimo uso
- **THEN** bot envia painel normalmente

### Requirement: Botao Menu em toda resposta publica do bot

Toda View publica do bot SHALL incluir um botao "Menu" persistente. Ao clicar, o bot SHALL enviar o menu contextual completo como mensagem ephemeral, com os mesmos botoes que o comando `/menu` exibiria para o contexto atual da campanha.

#### Scenario: Botao Menu apos rolagem

- **WHEN** jogador ou GM executa roll com sucesso
- **THEN** PostRollView inclui botao "Menu" alem dos botoes existentes (Roll, Undo, etc.)
- **WHEN** usuario clica "Menu"
- **THEN** bot envia menu contextual completo como mensagem ephemeral

#### Scenario: Botao Menu apos acao de doom

- **WHEN** GM executa acao de doom com sucesso
- **THEN** PostDoomActionView inclui botao "Menu"
- **WHEN** GM clica "Menu"
- **THEN** bot envia menu contextual como mensagem ephemeral

#### Scenario: Botao Menu apos acao de state

- **WHEN** GM executa stress add, asset add, ou complication add com sucesso
- **THEN** View de resposta inclui botao "Menu"

#### Scenario: Botao Menu em mensagem do proprio /menu

- **WHEN** usuario executa /menu
- **THEN** mensagem do menu SHALL NOT incluir botao "Menu" adicional (evita redundancia)

#### Scenario: Botao Menu persiste apos restart

- **WHEN** bot reinicia e usuario clica "Menu" em mensagem anterior
- **THEN** bot processa normalmente e envia menu contextual ephemeral
