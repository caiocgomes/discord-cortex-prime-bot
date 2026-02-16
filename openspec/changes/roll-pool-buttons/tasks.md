## 1. Helpers genéricos em views/base.py

- [x] 1.1 Criar `add_die_buttons(view, callback)` que gera 5 botões (d4-d12) numa ActionRow com callback parametrizado por die_size
- [x] 1.2 Criar `add_player_options(view, players, callback)` que usa botões quando <= 5, select quando > 5
- [x] 1.3 Testes unitários para helpers: verificar que add_die_buttons cria 5 botões, add_player_options faz threshold correto

## 2. Dice pool modal (rolling_views.py)

- [x] 2.1 Extrair lógica de rolagem duplicada (DicePoolSelectView._execute_roll e AssetIncludeSelectView._execute_roll) para função compartilhada `execute_player_roll(db, campaign_id, player_id, player_name, pool, included_assets)`
- [x] 2.2 Criar classe `DicePoolModal(discord.ui.Modal)` com TextInput para dados e TextInput opcional para assets
- [x] 2.3 Implementar `DicePoolModal.on_submit`: parse_dice_notation no campo de dados, resolução de assets por nome, chamada a execute_player_roll
- [x] 2.4 Alterar `RollStartButton.callback` para abrir DicePoolModal em vez de DicePoolSelectView. Buscar assets do jogador para popular placeholder dinâmico
- [x] 2.5 Remover classes DicePoolSelectView e AssetIncludeSelectView (substituídas pelo modal)
- [x] 2.6 Testes: modal com notação válida, notação inválida, assets encontrados, assets não encontrados, campo de assets vazio

## 3. Botões de dado nas chains de state (state_views.py)

- [x] 3.1 Substituir StressDieSelectView.add_die_select por add_die_buttons, callback chama _on_die_selected(interaction, die_size)
- [x] 3.2 Substituir AssetDieSelectView.add_die_select por add_die_buttons
- [x] 3.3 Substituir CompDieSelectView.add_die_select por add_die_buttons
- [x] 3.4 Substituir StressPlayerSelectView.add_player_select por add_player_options
- [x] 3.5 Substituir AssetOwnerSelectView.add_owner_select por add_player_options (manter opção "Asset de Cena" como botão adicional)
- [x] 3.6 Substituir CompTargetSelectView.add_target_select por add_player_options (manter opção "Complicacao de Cena" como botão adicional)
- [x] 3.7 Substituir StressTypeSelectView.add_type_select por botões dinâmicos (1 botão por tipo de stress)
- [x] 3.8 Testes: chain de stress completa com botões, chain de asset completa, chain com > 5 jogadores usa select

## 4. Botões de dado no doom (doom_views.py)

- [x] 4.1 Substituir DoomDieSelectView.add_die_select por add_die_buttons
- [x] 4.2 Substituir DoomRemoveSelectView.add_die_select por botões dinâmicos (1 botão por tamanho presente no pool, deduplicado)
- [x] 4.3 Testes: doom add com botões, doom remove com botões deduplicados

## 5. Comando /menu (cog novo)

- [x] 5.1 Criar cogs/menu.py com MenuCog e comando /menu
- [x] 5.2 Implementar lógica contextual: verificar campanha, cena ativa, doom habilitado, montar view com DynamicItems correspondentes
- [x] 5.3 Implementar cooldown de 10 segundos por usuário
- [x] 5.4 Registrar cog no bot.py (extensões carregadas no setup)
- [x] 5.5 Testes: /menu com cena ativa, sem cena, com doom, sem campanha, cooldown

## 6. Limpeza e verificação

- [x] 6.1 Remover imports e referências a classes eliminadas (DicePoolSelectView, AssetIncludeSelectView, add_die_select, add_player_select)
- [x] 6.2 Rodar suite completa de testes, verificar que testes existentes continuam passando
- [x] 6.3 Verificar que custom_ids de botões efêmeros usam uuid para evitar conflito entre views simultâneas
