## ADDED Requirements

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
