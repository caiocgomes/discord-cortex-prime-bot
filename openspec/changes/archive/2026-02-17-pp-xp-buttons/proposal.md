## Why

PP e XP só estão acessíveis via slash commands (`/pp add`, `/pp remove`, `/xp add`, `/xp remove`). Como o bot foi desenhado para funcionar inteiramente via botões para acessibilidade (GM cego usando screen reader), essa lacuna obriga digitação para operações frequentes de sessão. PP em particular muda constantemente durante gameplay.

## What Changes

- Adicionar botão PP ao menu e às views contextuais. O fluxo via botão: selecionar jogador (GM escolhe, jogador é auto-selecionado) → apresentar dois botões (up/down) que adicionam ou removem 1 PP por clique.
- Adicionar botão XP ao menu e às views contextuais. O fluxo via botão: selecionar jogador (GM escolhe, jogador obtém o próprio automaticamente) → abrir modal Discord para digitar quantidade → executar add.
- Os slash commands existentes permanecem como interface paralela completa.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `gm-button-views`: Adicionar button chains para PP (player select → up/down) e XP (player select → modal de quantidade). Inclui DynamicItems persistentes e verificação de permissão.
- `action-menu`: Adicionar botões PP e XP ao painel do `/menu` quando há cena ativa.

## Impact

- `src/cortex_bot/views/state_views.py`: Novos DynamicItems para PP e XP flows.
- `src/cortex_bot/views/common.py`: Possível adição de botões PP/XP aos PostActionViews.
- `src/cortex_bot/cogs/menu.py` ou equivalente: Adicionar botões ao painel do /menu.
- `src/cortex_bot/bot.py`: Registrar novos DynamicItems no setup_hook.
- `tests/test_views.py`: Testes para os novos flows.
