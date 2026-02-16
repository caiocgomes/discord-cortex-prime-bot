## 1. Projeto e infraestrutura

- [x] 1.1 Inicializar projeto Python com uv (pyproject.toml, dependências: discord.py, aiosqlite)
- [x] 1.2 Criar estrutura de diretórios (bot.py, cogs/, models/, services/, config.py)
- [x] 1.3 Criar config.py com carregamento de token e DB path via variáveis de ambiente
- [x] 1.4 Criar bot.py com setup do discord.py, carregamento de cogs, evento on_ready

## 2. Banco de dados e modelos

- [x] 2.1 Criar models/database.py com schema SQLite (campaigns, players, stress_types, scenes, assets, stress, trauma, complications, hero_dice, doom_pool_dice, crisis_pools, crisis_pool_dice, action_log)
- [x] 2.2 Implementar inicialização do banco (create tables, WAL mode, foreign keys)
- [x] 2.3 Criar models/dice.py com utilities de dados (validação d4-d12, step up, step down, parsing de notação "1d8 2d6")

## 3. Serviços core

- [x] 3.1 Criar services/formatter.py com formatação de texto acessível (resultados de rolagem, info de campanha, confirmações de ação)
- [x] 3.2 Criar services/state_manager.py com operações de estado que gravam action_log (add/remove/step up/step down com dados de undo)
- [x] 3.3 Criar services/roller.py com lógica de rolagem (rolar pool, identificar hitches/botches, calcular combinações best mode, comparar com dificuldade, detectar heroic success)

## 4. Campaign lifecycle (cog)

- [x] 4.1 Implementar `/setup` com parâmetros: name, players (menções), stress_types, doom_pool, hero_dice, trauma, best_mode
- [x] 4.2 Implementar vinculação jogador/Discord ID e registro de GM automático
- [x] 4.3 Implementar verificação de permissões (jogador vs GM) como decorator/check reutilizável
- [x] 4.4 Implementar `/info` com output textual acessível do estado completo da campanha
- [x] 4.5 Implementar `/campaign end` com confirmação e remoção de dados

## 5. Scene management (cog)

- [x] 5.1 Implementar `/scene start` com nome opcional, validação de cena única ativa
- [x] 5.2 Implementar `/scene end` com limpeza automática (assets de cena, complications de cena, crisis pools)
- [x] 5.3 Implementar opção bridge em `/scene end` com step down automático de stress (d4 eliminado)
- [x] 5.4 Implementar resumo textual de transição de cena (removidos, persistentes, mudanças de stress)
- [x] 5.5 Implementar `/scene info` com estado da cena ativa

## 6. State tracking (cog)

- [x] 6.1 Implementar `/asset` com subcomandos add, stepup, stepdown, remove (parâmetros: name, die, duration, scene_asset, player)
- [x] 6.2 Implementar `/stress` com subcomandos add, stepup, stepdown, remove (parâmetros: player, type, die) com regras de substituição/step up do Cortex
- [x] 6.3 Implementar `/trauma` com subcomandos add, stepup, stepdown, remove (condicional ao módulo trauma habilitado)
- [x] 6.4 Implementar `/complication` com subcomandos add, stepup, stepdown, remove (parâmetros: player, name, die, scene)
- [x] 6.5 Implementar `/pp` com subcomandos add, remove (parâmetros: player, amount)
- [x] 6.6 Implementar `/xp` com subcomandos add, remove (parâmetros: player, amount)
- [x] 6.7 Implementar `/hero` com subcomandos bank, use (condicional ao módulo hero dice habilitado)
- [x] 6.8 Implementar autocomplete para parâmetros de player, asset name, stress type em todos os comandos

## 7. Dice rolling (cog)

- [x] 7.1 Implementar `/roll` com parâmetros: dice, include, difficulty, extra
- [x] 7.2 Integrar sugestão de elementos rastreados no resultado (assets disponíveis, stress/complications da oposição)
- [x] 7.3 Implementar best mode com cálculo de todas as combinações de 2 dados para total + 1 para effect
- [x] 7.4 Implementar comparação com dificuldade (sucesso, falha, heroic success com step up de effect die)
- [x] 7.5 Implementar identificação de hitches e botches com mensagens contextuais
- [x] 7.6 Implementar gasto automático de PP para dados extras

## 8. Doom e crisis pools (cog)

- [x] 8.1 Implementar `/doom` com subcomandos add, remove, stepup, stepdown (condicional ao módulo doom pool)
- [x] 8.2 Implementar `/doom roll` (completo ou parcial) com sugestão de dificuldade
- [x] 8.3 Implementar `/doom spend` para gastar dado do doom pool no total de dificuldade
- [x] 8.4 Implementar `/crisis` com subcomandos add, remove, roll (vinculado à cena ativa)

## 9. Undo (cog)

- [x] 9.1 Implementar `/undo` que reverte última ação de estado do autor (ou qualquer ação se GM)
- [x] 9.2 Garantir que rolagens e transições de cena não entram no log de undo
- [x] 9.3 Implementar confirmação textual do que foi desfeito

## 10. Testes e validação

- [x] 10.1 Testes unitários para services/roller.py (combinações, hitches, heroic success, best mode)
- [x] 10.2 Testes unitários para services/state_manager.py (operações de estado com undo)
- [x] 10.3 Testes unitários para models/dice.py (step up/down, parsing, validação)
- [x] 10.4 Testes de integração para fluxo completo: setup → cena → rolagem → transição → undo
