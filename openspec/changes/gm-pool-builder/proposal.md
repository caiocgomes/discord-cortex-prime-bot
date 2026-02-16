## Why

O pool builder interativo (botoes) funciona para jogadores mas nao oferece contexto para o GM. Quando o GM clica Roll, ve os mesmos botoes de dado sem nenhuma informacao de stress, complications ou assets de cena. O GM precisa montar pools de oposicao com dados que o bot ja rastreia, e hoje precisa consultar /campaign info separadamente e digitar tudo via /gmroll. Unificar o pool builder para GM e jogador elimina esse atrito e mantem toda a informacao acessivel via NVDA no mesmo painel.

## What Changes

- Quando o GM clica Roll, o pool builder mostra stress e complications de todos os jogadores + complications de cena como botoes toggle (alem dos botoes de dado d4-d12)
- Label de cada toggle identifica o dono: "Alice: Physical d8", "Cena: Trapped d6"
- Jogador continua vendo apenas seus proprios assets como toggles (sem mudanca)
- O resultado da rolagem do GM identifica quais elementos de oposicao foram incluidos
- `/gmroll` continua funcionando como fallback via slash command

## Capabilities

### New Capabilities

### Modified Capabilities
- `dice-rolling`: Roll button abre pool builder com conteudo diferenciado por papel (GM vs jogador)
- `gm-roll`: GM passa a poder usar o pool builder interativo em vez de apenas /gmroll

## Impact

- `views/rolling_views.py`: RollStartButton.callback diferencia GM/jogador e busca dados diferentes; PoolBuilderView recebe items genéricos (assets OU stress/complications)
- `views/base.py`: nenhuma mudanca
- `models/database.py`: pode precisar de query para buscar todas complications de cena
- `tests/test_views.py`: novos testes para pool builder GM
