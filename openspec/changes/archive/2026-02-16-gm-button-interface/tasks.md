## 1. Infraestrutura de views

- [x] 1.1 Criar módulo `src/cortex_bot/views/` com `__init__.py` e `base.py` contendo `CortexView(discord.ui.View)` com `timeout=None`
- [x] 1.2 Implementar helpers em `base.py`: parsing de custom_id (`cortex:{action}:{params}`), verificação de GM permission no callback, resposta efêmera de permissão negada
- [x] 1.3 Criar função `register_persistent_views(bot)` em `views/__init__.py` que registra todas as views e DynamicItems
- [x] 1.4 Integrar `register_persistent_views` no `setup_hook` de `bot.py`, antes do carregamento de cogs
- [x] 1.5 Adicionar testes para parsing de custom_id e verificação de permissão nos callbacks

## 2. Views de scene

- [x] 2.1 Criar `views/scene_views.py` com `PostSetupView` (botão Scene Start) e `PostSceneEndView` (botões Scene Start, Campaign Info)
- [x] 2.2 Criar `PostSceneStartView` com botões Roll, Stress Add, Asset Add, Complication Add, e Doom Add condicional
- [x] 2.3 Integrar views no cog `scene.py`: anexar view ao `send_message`/`followup.send` de cada resposta de sucesso
- [x] 2.4 Integrar `PostSetupView` no cog `campaign.py` na resposta de setup
- [x] 2.5 Adicionar testes para scene views (botões presentes, doom condicional, custom_ids corretos)

## 3. Views de rolling

- [x] 3.1 Criar `views/rolling_views.py` com `PostRollView` (botões Roll, Undo)
- [x] 3.2 Implementar select chain de Roll: select de dados (d4-d12 com quantidade), select de assets do jogador para include, select de dificuldade opcional
- [x] 3.3 Integrar PostRollView no cog `rolling.py` nas respostas de `/roll` e `/gmroll`
- [x] 3.4 Adicionar testes para rolling views e select chain

## 4. Views de state (stress/asset/complication)

- [x] 4.1 Criar `views/state_views.py` com `PostStateActionView` (botões Undo + repetir ação)
- [x] 4.2 Implementar select chain de Stress Add: select jogador → select tipo stress → select dado → executa via StateManager
- [x] 4.3 Implementar select chain de Asset Add: select jogador/cena → input nome → select dado → executa via StateManager
- [x] 4.4 Implementar select chain de Complication Add: select jogador/cena → input nome → select dado → executa via StateManager
- [x] 4.5 Integrar views no cog `state.py`: anexar PostStateActionView a cada resposta de sucesso dos grupos stress, asset e complication
- [x] 4.6 Adicionar testes para state views e select chains

## 5. Views de doom e crisis

- [x] 5.1 Criar `views/doom_views.py` com `PostDoomActionView` (botões Doom Add, Doom Remove, Doom Roll) e `PostCrisisActionView`
- [x] 5.2 Implementar select chain de Doom Add: select dado → executa
- [x] 5.3 Integrar views no cog `doom.py`: anexar views condicionalmente (só se doom_pool habilitado)
- [x] 5.4 Adicionar testes para doom views

## 6. Views comuns (undo, info)

- [x] 6.1 Criar `views/common.py` com `UndoButton` (DynamicItem) e `CampaignInfoButton` (DynamicItem) reutilizáveis entre views
- [x] 6.2 Implementar callback do UndoButton que executa undo direto com verificação de permissão
- [x] 6.3 Integrar `PostInfoView` em campaign.py info e scene.py info (botão Roll se cena ativa, Scene Start se não)
- [x] 6.4 Integrar view no cog `undo.py`: anexar botões Undo (outro) e Campaign Info
- [x] 6.5 Adicionar testes para common views e DynamicItems

## 7. Teste de integração

- [x] 7.1 Criar teste de integração que simula flow completo via botões: setup → scene start → stress add chain → roll chain → undo → scene end
- [x] 7.2 Verificar que todas as views são registradas corretamente no setup_hook (teste de registro)
- [x] 7.3 Verificar que botões em mensagens pré-restart continuam funcionais (teste de persistência com custom_id parsing)
