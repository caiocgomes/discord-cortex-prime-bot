## Why

O output de rolagem esconde informação crítica para decisão do jogador e o fluxo pós-rolagem exige navegação desnecessária. Quando best_mode está ativo, os resultados individuais dos dados não aparecem, impedindo o jogador de avaliar se vale gastar PP para somar um terceiro dado. O GM precisa navegar para longe da mensagem de rolagem para lidar com hitches ou rolar o doom pool. E os botões de ação desaparecem entre mensagens, forçando o uso repetido de `/menu`.

## What Changes

- Corrigir o formatter para sempre exibir todos os resultados individuais dos dados antes das best options (bug fix)
- Adicionar botões interativos pós-rolagem para o GM resolver hitches: criar complicação em um jogador (com seleção de alvo e nome) ou adicionar d6 ao doom pool
- Adicionar botão de Doom Roll na PostRollView quando doom_pool está habilitado, permitindo o GM rolar a oposição direto da mesma mensagem
- Toda saída do bot termina com os botões do menu contextual, eliminando a necessidade de chamar `/menu` manualmente

## Capabilities

### New Capabilities
- `hitch-actions`: Fluxo interativo pós-rolagem para o GM resolver hitches via botões: criar complicação em jogador alvo (seleção de jogador + nome da complicação + PP automático) ou adicionar dado ao doom pool.

### Modified Capabilities
- `dice-rolling`: Corrigir bug que omite resultados individuais quando best_mode está ativo. Todos os dados devem aparecer antes das best options.
- `action-menu`: Botões do menu contextual passam a ser anexados automaticamente a toda resposta do bot, não apenas via `/menu`.
- `gm-button-views`: PostRollView ganha botão Doom Roll (quando doom habilitado). Hitch action buttons aparecem quando a rolagem produziu hitches.

## Impact

- `services/formatter.py`: Inserir linha de resultados individuais antes do bloco de best options
- `views/rolling_views.py`: PostRollView condicional com botões de hitch actions e doom roll. Novo fluxo de seleção de jogador + input de nome para complicação.
- `views/doom_views.py`: DoomRollButton reutilizado ou adaptado para contexto pós-rolagem
- Todos os cogs e views que enviam mensagens: anexar menu contextual ao final de cada resposta
- `cogs/rolling.py`: Passar informação de hitches para a PostRollView
- `services/state_manager.py`: Método para criar complicação + dar PP em uma operação atômica (se não existir)
