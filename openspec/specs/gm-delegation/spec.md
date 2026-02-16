## ADDED Requirements

### Requirement: GM pode promover jogador a delegado
O GM SHALL poder conceder permissões de delegado a qualquer jogador registrado na campanha via `/campaign delegate player:@Jogador`. O delegado MUST manter seu registro de jogador intacto (stress, assets, PP, XP, complications).

#### Scenario: Delegação bem-sucedida
- **WHEN** o GM executa `/campaign delegate player:@Bob`
- **THEN** Bob recebe `is_delegate=1` e uma mensagem de confirmação é exibida

#### Scenario: Tentativa de delegação por não-GM
- **WHEN** um jogador sem `is_gm` executa `/campaign delegate player:@Bob`
- **THEN** o comando retorna erro "Apenas o GM pode executar este comando."

#### Scenario: Delegação de jogador inexistente
- **WHEN** o GM executa `/campaign delegate player:@Desconhecido` e o usuário não está registrado na campanha
- **THEN** o comando retorna erro indicando que o jogador não está na campanha

#### Scenario: Delegação do próprio GM
- **WHEN** o GM executa `/campaign delegate player:@GM` (ele mesmo)
- **THEN** o comando retorna erro indicando que o GM já possui todas as permissões

### Requirement: GM pode revogar delegação
O GM SHALL poder revogar permissões de delegado via `/campaign undelegate player:@Jogador`.

#### Scenario: Revogação bem-sucedida
- **WHEN** o GM executa `/campaign undelegate player:@Bob` e Bob é delegado
- **THEN** Bob perde `is_delegate=1` e uma mensagem de confirmação é exibida

#### Scenario: Revogação de jogador que não é delegado
- **WHEN** o GM executa `/campaign undelegate player:@Alice` e Alice não é delegada
- **THEN** o comando retorna erro indicando que o jogador não é delegado

### Requirement: Delegado tem acesso a comandos GM-only
O delegado SHALL ter acesso aos mesmos comandos que o GM, exceto `/campaign campaign_end`. Todos os checks de permissão que usam `is_gm` MUST ser atualizados para aceitar `is_gm OR is_delegate`, exceto para encerramento de campanha.

#### Scenario: Delegado adiciona stress a outro jogador
- **WHEN** o delegado executa `/stress add player:@Alice type:Physical die:d8`
- **THEN** o stress é adicionado normalmente, logado com o discord_id do delegado

#### Scenario: Delegado gerencia doom pool
- **WHEN** o delegado executa `/doom add die:d8`
- **THEN** o dado é adicionado ao doom pool normalmente

#### Scenario: Delegado inicia cena
- **WHEN** o delegado executa `/scene start name:Taverna`
- **THEN** a cena é criada normalmente

#### Scenario: Delegado tenta encerrar campanha
- **WHEN** o delegado executa `/campaign campaign_end confirm:sim`
- **THEN** o comando retorna erro "Apenas o GM pode executar este comando."

#### Scenario: Delegado faz undo global
- **WHEN** o delegado executa `/undo`
- **THEN** o sistema desfaz a última ação de qualquer jogador (mesmo comportamento do GM)

### Requirement: Delegado mantém estado de jogador no bridge scene
Durante bridge scene (fim de cena com `bridge:true`), o sistema MUST aplicar step down de stress no delegado como em qualquer jogador. Apenas `is_gm` é pulado.

#### Scenario: Bridge scene com delegado
- **WHEN** a cena termina com `bridge:true` e o delegado tem stress Physical d8
- **THEN** o stress do delegado é reduzido para d6 (step down normal)

### Requirement: Delegado visível no campaign info
O `/campaign info` SHALL exibir "(delegado)" ao lado do nome de jogadores com `is_delegate=1`.

#### Scenario: Campaign info com delegado
- **WHEN** `/campaign info` é executado e Bob é delegado
- **THEN** a saída mostra "Bob (delegado):" em vez de "Bob:"

### Requirement: Delegado não pode delegar
Apenas o GM original (`is_gm=1`) pode conceder e revogar delegações. Delegados não possuem essa capacidade.

#### Scenario: Delegado tenta delegar outro jogador
- **WHEN** o delegado executa `/campaign delegate player:@Alice`
- **THEN** o comando retorna erro "Apenas o GM pode executar este comando."
