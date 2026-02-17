## 1. PP Button Chain

- [x] 1.1 Criar PPStartButton (DynamicItem) em state_views.py com template regex `cortex:pp_start:{campaign_id}`. Callback: verifica registro na campanha, se GM/delegate apresenta player select via add_player_options, se jogador vai direto para up/down.
- [x] 1.2 Criar PPPlayerSelectView com callback que apresenta botões PP +1 e PP -1 para o jogador selecionado.
- [x] 1.3 Criar PPAdjustView com botões +1 e -1. Callback de +1 chama StateManager.update_pp(delta=+1), edita mensagem ephemeral com resultado, envia followup público. Callback de -1 chama update_pp(delta=-1), trata erro "insufficient" mantendo botões ativos.
- [x] 1.4 Criar PostPPView com botões contextuais após ação PP (PPStartButton + UndoButton).

## 2. XP Button Chain

- [x] 2.1 Criar XPStartButton (DynamicItem) em state_views.py com template regex `cortex:xp_start:{campaign_id}`. Callback: verifica registro, se GM/delegate apresenta player select, se jogador abre modal direto.
- [x] 2.2 Criar XPPlayerSelectView com callback que abre XPAmountModal para o jogador selecionado.
- [x] 2.3 Criar XPAmountModal (discord.ui.Modal) com TextInput para quantidade. On submit: validar numero positivo, chamar StateManager.update_xp, editar/enviar resultado com PostXPView.
- [x] 2.4 Criar PostXPView com botões contextuais após ação XP (XPStartButton + UndoButton).

## 3. Integração

- [x] 3.1 Adicionar PPStartButton e XPStartButton ao MenuView (quando has_active_scene=True).
- [x] 3.2 Registrar PPStartButton e XPStartButton como DynamicItems no setup_hook do bot.py.

## 4. Testes

- [x] 4.1 Testes para PPStartButton: GM vê player select, jogador vai direto para adjust.
- [x] 4.2 Testes para PPAdjustView: +1 incrementa, -1 decrementa, -1 com 0 PP retorna erro.
- [x] 4.3 Testes para XPStartButton: GM vê player select, jogador abre modal direto.
- [x] 4.4 Testes para XPAmountModal: quantidade válida executa add, quantidade inválida retorna erro.
