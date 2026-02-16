## ADDED Requirements

### Requirement: Comando /menu exibe painel de ações contextuais

O bot SHALL disponibilizar comando `/menu` que gera uma mensagem pública (não efêmera) contendo botões DynamicItem baseados no estado atual da campanha no canal. A mensagem SHALL ser pinável pelo GM. Os botões SHALL ser os mesmos DynamicItem já registrados no bot (RollStartButton, StressAddStartButton, etc.), reutilizando custom_ids existentes.

#### Scenario: /menu com cena ativa e doom habilitado

- **WHEN** GM executa `/menu` em canal com campanha ativa, cena ativa, e doom_pool habilitado
- **THEN** bot envia mensagem pública com texto descritivo incluindo nome da cena
- **AND** Row 1 contém botões: Roll, Stress Add, Asset Add, Complication Add, Undo
- **AND** Row 2 contém botões: Doom Add, Doom Remove, Doom Roll, Campaign Info

#### Scenario: /menu com cena ativa sem doom

- **WHEN** GM executa `/menu` em canal com campanha ativa e cena ativa, sem doom_pool
- **THEN** bot envia mensagem pública com botões: Roll, Stress Add, Asset Add, Complication Add, Undo, Campaign Info
- **AND** nenhum botão de doom aparece

#### Scenario: /menu sem cena ativa

- **WHEN** GM executa `/menu` em canal com campanha ativa mas sem cena ativa
- **THEN** bot envia mensagem pública com botões: Scene Start, Campaign Info

#### Scenario: /menu sem campanha

- **WHEN** usuário executa `/menu` em canal sem campanha ativa
- **THEN** bot responde com mensagem de erro informando que não há campanha no canal

#### Scenario: Qualquer jogador pode usar /menu

- **WHEN** jogador (não GM) executa `/menu` em canal com campanha ativa
- **THEN** bot envia mensagem pública com botões contextuais
- **AND** permissão de cada botão é verificada no callback, não no /menu

### Requirement: /menu tem cooldown para evitar spam

O comando `/menu` SHALL ter cooldown de 10 segundos por usuário para evitar spam de mensagens com botões no canal.

#### Scenario: Cooldown ativo

- **WHEN** GM executa `/menu` e executa novamente antes de 10 segundos
- **THEN** bot responde com mensagem efêmera informando o cooldown restante

#### Scenario: Cooldown expirado

- **WHEN** GM executa `/menu` após 10 segundos do último uso
- **THEN** bot gera nova mensagem com painel normalmente

### Requirement: Botões do /menu são persistentes

Os botões gerados pelo `/menu` SHALL usar DynamicItem com `timeout=None` e custom_ids com campaign_id, identicos aos botões já usados em post-action views. Os botões SHALL funcionar após restart do bot e independente de a mensagem estar pinada.

#### Scenario: Botão do /menu funciona após restart

- **WHEN** GM executa `/menu`, pina a mensagem, e bot reinicia
- **AND** GM clica um botão na mensagem pinada
- **THEN** bot processa a interação normalmente

#### Scenario: Botão do /menu funciona sem pin

- **WHEN** GM executa `/menu` sem pinar a mensagem
- **AND** GM clica um botão na mensagem (se ainda visível no chat)
- **THEN** bot processa a interação normalmente
