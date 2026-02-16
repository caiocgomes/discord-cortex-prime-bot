## Why

Os select menus do Discord são problemáticos com NVDA, o screen reader dominante entre usuários cegos no Windows. Existe um bug documentado (nvaccess/nvda#18224) onde `aria-selected="true"` não é anunciado pelo NVDA em combobox/listbox, o que significa que o usuário não tem feedback confiável de quais opções marcou. O multi-select usado na montagem de dice pool é ainda pior: sem feedback de estado, sem anúncio de mudança, interação confusa. Selects de valor único (escolher UM jogador, UM tipo de stress) também sofrem do mesmo problema de estado não anunciado, embora sejam funcionalmente mais simples.

Além disso, os botões contextuais pós-ação só existem grudados na resposta da última ação do bot. Quando o chat rola (o que acontece a cada 2-3 minutos em sessão ativa com 4-6 jogadores), o GM perde acesso ao painel e precisa digitar slash commands para recuperá-lo.

O Discord também não implementa aria-live regions em mensagens editadas, o que significa que abordagens incrementais (clicar botão, bot edita mensagem, clicar outro botão) não geram feedback automático no NVDA. O usuário não ouve o que mudou.

## What Changes

### 1. Dice pool via Modal com TextInput (substituindo multi-select)

Substituir o `DicePoolSelectView` (select multi-value) por um botão "Montar Pool" que abre um Discord Modal com TextInput. O jogador digita a notação que já existe (`2d8 1d6 1d10`). O parser `parse_dice_notation` em `models/dice.py` já valida e processa essa notação. Um segundo campo opcional no modal lista os assets ativos do jogador no placeholder/hint, e o jogador digita os nomes dos que quer incluir.

Justificativa: o NVDA faz auto-switch para focus mode ao encontrar TextInput dentro de modal. Focus trap funciona. São 3 interações para qualquer pool (clicar botão, digitar, confirmar), sem perda de foco, sem re-render, sem estado incremental.

### 2. Selects de valor único -> botões (onde <= 5 opções)

Trocar selects por botões dinâmicos em todas as chains onde a seleção é de valor único e o número de opções é pequeno:

- Seleção de dado (d4, d6, d8, d10, d12): 5 botões, 1 row. Usado em stress add, asset add, complication add, doom add.
- Seleção de tipo de stress (Physical, Mental, etc.): 2-4 botões, 1 row.
- Seleção de doom die (d4-d12): 5 botões, 1 row. Já tem poucas opções.

Para seleção de jogador (pode ter > 5): botões quando <= 5 jogadores, fallback para select quando > 5. O NVDA anuncia cada botão como "Alice button", "Bob button", o que é mais claro que navegar um select cuja seleção não é anunciada.

Selects permanecem para listas longas: nomes de asset (common names), nomes de complication (common names), e qualquer caso com > 5 opções que não caibam em 1 row.

### 3. `/menu` para painel de ações recuperável

Comando `/menu` que exibe painel de ações baseado no estado atual da campanha. O painel é uma mensagem pública (não efêmera) com botões DynamicItem, que o GM pode pinar no canal. O bot não atualiza a mensagem automaticamente (evita o problema de aria-live), mas os botões são persistentes e sempre funcionais.

Conteúdo do painel depende do estado:
- Sem cena ativa: Scene Start, Campaign Info
- Com cena ativa: Roll, Stress Add, Asset Add, Complication Add, Undo, Campaign Info
- Com doom habilitado: Doom Add, Doom Remove, Doom Roll (adicionais)

### 4. Slash commands com autocomplete preservados

Os slash commands existentes continuam sendo a interface primária para ações complexas e nomes customizados. O autocomplete do Discord funciona bem com NVDA. Os botões são uma camada de conveniência, não substituição.

## Capabilities

### New Capabilities

- `action-menu`: Comando `/menu` que exibe painel de ações contextuais como mensagem pública pinável. Botões DynamicItem persistentes.
- `dice-pool-modal`: Modal com TextInput para montagem de dice pool usando notação existente. Campo opcional para inclusão de assets.

### Modified Capabilities

- `gm-button-views`: Select chains de valor único substituídas por botões dinâmicos onde <= 5 opções (dados, stress types, doom). Seleção de jogador usa botões quando <= 5, select quando > 5.

## Impact

- `src/cortex_bot/views/rolling_views.py`: Substituir `DicePoolSelectView` (multi-select) por `DicePoolModal` (TextInput). Substituir `AssetIncludeSelectView` (select) por campo no modal. Manter `RollStartButton` como trigger.
- `src/cortex_bot/views/state_views.py`: `StressTypeSelectView` e `StressDieSelectView` viram views com botões. `StressPlayerSelectView` usa botões quando <= 5 jogadores, select quando > 5. Mesma lógica para `AssetOwnerSelectView`, `CompTargetSelectView`, `AssetDieSelectView`, `CompDieSelectView`.
- `src/cortex_bot/views/doom_views.py`: `DoomDieSelectView` vira botões (5 opções fixas).
- Novo cog ou comando em cog existente para `/menu`.
- Limite de 25 componentes por mensagem (5 rows x 5 buttons) respeitado em todos os cenários.

## Constraints

- O NVDA não anuncia `aria-selected` em selects do Discord (bug confirmado). Não usar multi-select.
- O Discord não implementa aria-live em mensagens editadas. Não usar padrões incrementais que dependam de re-render para feedback.
- Modals do Discord suportam até 5 componentes (rows). Cada TextInput ocupa 1 row.
- ActionRow do Discord não anuncia agrupamento semântico no NVDA. Botões são navegados linearmente via Tab.
- Máximo 5 botões por row, 5 rows por mensagem.
