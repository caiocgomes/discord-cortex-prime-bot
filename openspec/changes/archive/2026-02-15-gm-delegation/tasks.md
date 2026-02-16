## 1. Schema e modelo de dados

- [x] 1.1 Adicionar coluna `is_delegate INTEGER NOT NULL DEFAULT 0` à tabela `players` no SCHEMA em `models/database.py`
- [x] 1.2 Adicionar migration inline no `Database.initialize()` com `ALTER TABLE players ADD COLUMN is_delegate` (try/except para idempotência)

## 2. Helper de permissão

- [x] 2.1 Criar função `has_gm_permission(player: dict) -> bool` que retorna `player["is_gm"] or player.get("is_delegate", 0)` (localização: utils ou dentro dos cogs como helper compartilhado)
- [x] 2.2 Atualizar checks de permissão em `cogs/state.py` para usar `has_gm_permission` em vez de `actor["is_gm"]` direto
- [x] 2.3 Atualizar checks de permissão em `cogs/scene.py` para usar `has_gm_permission` (exceto bridge scene que continua checando `is_gm` direto)
- [x] 2.4 Atualizar checks de permissão em `cogs/doom.py` para usar `has_gm_permission`
- [x] 2.5 Atualizar checks de permissão em `cogs/undo.py` para usar `has_gm_permission`

## 3. Comandos delegate/undelegate

- [x] 3.1 Adicionar subcomando `/campaign delegate player:@Jogador` em `cogs/campaign.py` (GM-only via `is_gm`, não `has_gm_permission`)
- [x] 3.2 Adicionar subcomando `/campaign undelegate player:@Jogador` em `cogs/campaign.py` (GM-only)
- [x] 3.3 Validações: jogador existe na campanha, não é o próprio GM, target já é/não é delegado

## 4. Formatter

- [x] 4.1 Atualizar `format_campaign_info` em `services/formatter.py` para exibir "(delegado)" ao lado do nome de jogadores com `is_delegate=1`

## 5. Comando /gmroll

- [x] 5.1 Implementar comando `/gmroll` em `cogs/rolling.py` com parâmetros `dice` (required), `name` (optional, default "GM"), `difficulty` (optional)
- [x] 5.2 Restringir a `has_gm_permission` com mensagem de erro adequada
- [x] 5.3 Reutilizar `roll_pool`, `find_hitches`, `is_botch`, `calculate_best_options` do roller service
- [x] 5.4 Chamar `format_roll_result` com `player_name=name`, sem `available_assets`, sem `opposition_elements`, sem `included_assets`

## 6. Testes

- [x] 6.1 Testes para delegate/undelegate: concessão, revogação, validações de erro (não-GM tentando, jogador inexistente, auto-delegação, revogação de não-delegado)
- [x] 6.2 Testes para `has_gm_permission`: GM retorna True, delegado retorna True, player normal retorna False
- [x] 6.3 Testes para `/gmroll`: roll básico sem estado pessoal, com nome de NPC, sem nome (default GM), best_mode, difficulty, jogador comum bloqueado
- [x] 6.4 Testes para formatter atualizado: exibição de "(delegado)" no campaign info
- [x] 6.5 Testes de permissão: delegado executa comandos GM-only com sucesso, delegado bloqueado em campaign_end
- [x] 6.6 Teste de bridge scene: delegado recebe step down de stress, GM não recebe
