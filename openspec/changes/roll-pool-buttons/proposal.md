## Why

O select multi-value do Discord para montar dice pool tem dois problemas. Primeiro, o NVDA tem um bug conhecido (nvaccess/nvda#18224) onde `aria-selected="true"` nao e anunciado em combobox/listbox, tornando selecao multipla silenciosa para leitores de tela. Segundo, o modelo mental de "selecionar tudo de uma vez" nao casa com o fluxo natural de Cortex Prime, onde o jogador pensa em cada trait separadamente e vai montando o pool incrementalmente.

A proposta e substituir o select por um pool builder interativo com botoes. O jogador clica nos dados que quer adicionar (d4-d12), clica nos assets ativos para incluir, e quando o pool esta pronto clica "Rolar". Os labels dos botoes carregam o estado (quantidade ja adicionada, assets incluidos), permitindo navegacao com Tab + NVDA sem depender de aria-live.

As chains de GM (stress/asset/complication add) tambem se beneficiam: trocar selects de dado por 5 botoes individuais e selects de jogador por botoes quando <= 5 jogadores.

## What Changes

- Substituir `DicePoolSelectView` e `AssetIncludeSelectView` por um `PoolBuilderView` interativo com botoes de dado, botoes de asset, e controles (Rolar, Limpar, Remover ultimo)
- Extrair logica de rolagem duplicada para funcao compartilhada `execute_player_roll()`
- Substituir selects de dado (d4-d12) por 5 botoes nas chains de GM (stress, asset, comp, doom)
- Substituir selects de jogador por botoes quando <= 5 jogadores, manter select quando > 5
- Criar helpers genericos `add_die_buttons()` e `add_player_options()` em `views/base.py`
- Adicionar comando `/menu` com painel contextual de acoes (Roll, Stress Add, etc.)

## Capabilities

### New Capabilities
- `pool-builder`: Interface de botoes para montagem incremental de dice pool com estado nos labels, toggle de assets, e controles de edicao
- `action-menu`: Comando /menu que apresenta painel contextual com botoes de acao baseado no estado da campanha

### Modified Capabilities
- `gm-button-views`: Chains de parametro (stress/asset/comp add, doom) passam a usar botoes em vez de selects para dado e jogador
- `dice-rolling`: Botao Roll abre pool builder em vez de select chain

## Impact

- `views/rolling_views.py`: reescrita quase completa (remove 2 classes, adiciona 1 classe + 1 funcao)
- `views/base.py`: adicao de helpers genericos (add_die_buttons, add_player_options)
- `views/state_views.py`: todas as views de chain refatoradas para usar helpers
- `views/doom_views.py`: views de doom refatoradas para usar helpers
- `cogs/menu.py`: novo cog
- `bot.py`: registro do novo cog
- `tests/test_views.py`: novos testes para pool builder, helpers, e menu
