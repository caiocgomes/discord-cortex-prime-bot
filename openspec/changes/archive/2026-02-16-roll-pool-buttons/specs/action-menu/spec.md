## ADDED Requirements

### Requirement: Comando /menu apresenta painel de acoes

O bot SHALL oferecer um comando `/menu` que envia mensagem publica com botoes de acao baseados no contexto atual da campanha. O jogador/GM pode fixar esta mensagem para acesso rapido.

#### Scenario: Menu com cena ativa

- **WHEN** GM executa /menu e campanha tem cena ativa
- **THEN** bot envia mensagem publica com botoes: Roll, Stress Add, Asset Add, Complication Add, Undo, Campaign Info
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
