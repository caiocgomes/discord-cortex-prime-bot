## Context

PP e XP são gerenciados via slash commands (`/pp add`, `/pp remove`, `/xp add`, `/xp remove`) que chamam `StateManager.update_pp()` e `StateManager.update_xp()`. Ambos aceitam `amount` (inteiro) e `player` (opcional, GM pode afetar outros). O bot já tem um padrão consolidado de button chains para operações multi-parâmetro (stress add, asset add, complication add) em `state_views.py`, usando DynamicItem persistentes com custom_id parseável por regex.

PP muda com frequência durante gameplay (a cada hitch, a cada uso de SFX), então o flow precisa ser rápido. XP muda raramente (fim de sessão), então aceita um fluxo com mais passos.

O projeto não usa `discord.ui.Modal` em lugar nenhum ainda. XP introduzirá o primeiro uso.

## Goals / Non-Goals

**Goals:**

- PP e XP acessíveis via botões no `/menu` e nos PostActionViews, sem precisar digitar slash commands.
- PP: flow otimizado para velocidade (up/down de 1 PP por clique, repetível).
- XP: flow com modal para quantidade arbitrária.
- Permissões: GM escolhe jogador, jogador opera apenas no próprio estado.
- Persistent buttons que sobrevivem restart do bot.

**Non-Goals:**

- PP em quantidade arbitrária via modal (o user descreveu explicitamente up/down de 1).
- XP remove via botão (operação rara, mantém slash command only).
- Modificar a lógica de negócio de PP/XP no StateManager (já funciona).

## Decisions

**PP flow usa up/down em vez de modal.** PP muda com frequência e quase sempre em incrementos de 1. Dois botões (PP +1 / PP -1) resolvem 95% dos casos sem abrir modal. Alternativa seria modal igual ao XP, mas adiciona fricção desnecessária para a operação mais comum da sessão.

**XP flow usa discord.ui.Modal para quantidade.** XP é distribuído em quantidades variáveis (1, 3, 5, etc.) e com pouca frequência. Um modal com campo numérico é mais adequado que botões de incremento. O modal é nativo do Discord, suporta validação, e o campo `TextInput` aceita `default` para sugerir valores.

**Player select: GM usa add_player_options, jogador pula direto.** Mesmo padrão de stress/asset/complication. Se o executor tem `has_gm_permission()`, apresenta seleção de jogadores (botões se <=5, select se >5). Se é jogador comum, opera em si mesmo sem etapa intermediária.

**PP up/down apresenta resultado inline e mantém botões.** Após clicar PP +1 ou PP -1, o bot edita a mensagem ephemeral com o novo total e mantém os botões ativos para novo clique. Isso permite ajustar PP rapidamente com múltiplos cliques sem reabrir o flow. O resultado final é postado publicamente só quando o user terminar (ou o ephemeral expirar naturalmente).

Alternativa considerada: postar público a cada clique. Descartada porque poluiria o canal com mensagens de +1/-1 durante sequências rápidas.

**PP up/down envia resultado público a cada ação.** Cada clique em +1 ou -1 edita a mensagem ephemeral com o resultado atualizado, mantendo os botões para continuar ajustando. A mensagem pública é enviada via followup para registrar cada mudança no canal, igual ao padrão de stress/asset/complication. Isso mantém consistência com o sistema de undo (cada ação gera um action_log) e transparência para outros jogadores.

**Botões PP e XP aparecem no menu quando há cena ativa.** O `/menu` com cena ativa já tem Roll, Stress Add, Asset Add, Complication Add, Undo, Campaign Info (+ Doom se habilitado). PP e XP serão adicionados como botões adicionais. Discord suporta até 25 componentes (5 rows de 5), e estamos em ~7 atualmente, então há espaço.

**Novos DynamicItems: PPStartButton, XPStartButton.** Seguem o padrão existente com template regex `cortex:pp_start:{campaign_id}` e `cortex:xp_start:{campaign_id}`. Registrados no `setup_hook` junto com os demais.

## Risks / Trade-offs

**Limite de componentes no Discord.** Cada View suporta no máximo 25 componentes (5 ActionRows de 5 itens). O menu com cena ativa + doom já usa ~8 botões. Adicionando PP e XP ficam ~10, dentro do limite. Se futuras features adicionarem mais botões, precisará reorganizar em rows ou usar paginação.

**PP up/down edita mensagem ephemeral.** Mensagens ephemeral têm timeout de ~15 minutos no Discord. Se o GM deixar o painel aberto por muito tempo sem interagir, o Discord pode invalidar o token de interação. Mitigação: o fluxo é rápido por natureza (ajustar PP e seguir em frente).

**Primeiro uso de Modal no projeto.** Introduz nova dependência de pattern (`discord.ui.Modal`, `TextInput`). O risco é baixo porque Modals são estáveis na API do Discord e não requerem persistent views (são efêmeros por natureza).
