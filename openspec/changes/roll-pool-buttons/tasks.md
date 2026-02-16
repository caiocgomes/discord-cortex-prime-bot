## 1. Helpers genericos em views/base.py

- [x] 1.1 Criar `add_die_buttons(view, callback)` que gera 5 botoes (d4-d12) numa ActionRow com callback parametrizado por die_size
- [x] 1.2 Criar `add_player_options(view, players, callback)` que usa botoes quando <= 5, select quando > 5
- [x] 1.3 Testes unitarios para helpers: verificar que add_die_buttons cria 5 botoes, add_player_options faz threshold correto

## 2. Pool builder (rolling_views.py)

- [x] 2.1 Extrair logica de rolagem duplicada (DicePoolSelectView._execute_roll e AssetIncludeSelectView._execute_roll) para funcao compartilhada `execute_player_roll(db, campaign_id, player_id, player_name, pool, included_assets)`
- [x] 2.2 Criar classe `PoolBuilderView(CortexView)` com estado interno: pool (list[int]), history (list para undo), included_assets (set[int]), assets_data (list[dict])
- [x] 2.3 Implementar `_rebuild()` que reconstroi todos os botoes com labels atualizados e faz edit_message
- [x] 2.4 Implementar botoes de dado: cada clique adiciona die_size ao pool e chama _rebuild
- [x] 2.5 Implementar botoes de asset: toggle on/off, adiciona/remove die_size do pool e chama _rebuild
- [x] 2.6 Implementar botao "Rolar N dados": valida pool nao vazio, chama execute_player_roll, envia resultado publico
- [x] 2.7 Implementar botao "Limpar": reseta pool, included_assets e history, chama _rebuild
- [x] 2.8 Implementar botao "Remover ultimo": remove ultimo item do history (dado ou asset toggle), chama _rebuild
- [x] 2.9 Alterar `RollStartButton.callback` para abrir PoolBuilderView em vez de DicePoolSelectView. Buscar assets do jogador para popular botoes
- [x] 2.10 Remover classes DicePoolSelectView e AssetIncludeSelectView (substituidas pelo pool builder)
- [x] 2.11 Testes: pool builder com adicao de dados, toggle de assets, remover ultimo, limpar, rolar com pool valido, rolar com pool vazio

## 3. Botoes de dado nas chains de state (state_views.py)

- [x] 3.1 Substituir StressDieSelectView.add_die_select por add_die_buttons, callback chama _on_die_selected(interaction, die_size)
- [x] 3.2 Substituir AssetDieSelectView.add_die_select por add_die_buttons
- [x] 3.3 Substituir CompDieSelectView.add_die_select por add_die_buttons
- [x] 3.4 Substituir StressPlayerSelectView.add_player_select por add_player_options
- [x] 3.5 Substituir AssetOwnerSelectView.add_owner_select por add_player_options (manter opcao "Asset de Cena" como botao adicional)
- [x] 3.6 Substituir CompTargetSelectView.add_target_select por add_player_options (manter opcao "Complicacao de Cena" como botao adicional)
- [x] 3.7 Substituir StressTypeSelectView.add_type_select por botoes dinamicos (1 botao por tipo de stress)
- [x] 3.8 Testes: chain de stress completa com botoes, chain de asset completa, chain com > 5 jogadores usa select

## 4. Botoes de dado no doom (doom_views.py)

- [x] 4.1 Substituir DoomDieSelectView.add_die_select por add_die_buttons
- [x] 4.2 Substituir DoomRemoveSelectView.add_die_select por botoes dinamicos (1 botao por tamanho presente no pool, deduplicado)
- [x] 4.3 Testes: doom add com botoes, doom remove com botoes deduplicados

## 5. Comando /menu (cog novo)

- [x] 5.1 Criar cogs/menu.py com MenuCog e comando /menu
- [x] 5.2 Implementar logica contextual: verificar campanha, cena ativa, doom habilitado, montar view com DynamicItems correspondentes
- [x] 5.3 Implementar cooldown de 10 segundos por usuario
- [x] 5.4 Registrar cog no bot.py (extensoes carregadas no setup)
- [x] 5.5 Testes: /menu com cena ativa, sem cena, com doom, sem campanha, cooldown

## 6. Limpeza e verificacao

- [x] 6.1 Remover imports e referencias a classes eliminadas (DicePoolSelectView, AssetIncludeSelectView, add_die_select, add_player_select)
- [x] 6.2 Rodar suite completa de testes, verificar que testes existentes continuam passando
- [x] 6.3 Verificar que custom_ids de botoes efemeros usam uuid para evitar conflito entre views simultaneas
