## 1. Fix: Resultados individuais no formatter

- [x] 1.1 Alterar `format_roll_result` em `services/formatter.py` para inserir linha com todos os resultados individuais (`_format_dice_detail`) antes do bloco de best_options
- [x] 1.2 Adicionar testes para verificar que todos os dados aparecem no output quando best_mode esta ativo (incluindo dados com hitch marcados)

## 2. Hitch action buttons

- [x] 2.1 Criar `HitchComplicationButton` (DynamicItem persistente) em `views/rolling_views.py`: abre chain de selecao de jogador + modal para nome da complicacao
- [x] 2.2 Criar `HitchDoomButton` (DynamicItem persistente) em `views/rolling_views.py`: adiciona d6 ao doom pool diretamente
- [x] 2.3 Criar modal `ComplicationNameModal` para input do nome da complicacao
- [x] 2.4 Implementar logica de criacao de complicacao d6 + concessao de 1 PP na callback do modal (com step up se complicacao ja existe, duas entries no action_log)
- [x] 2.5 Alterar `PostRollView` para aceitar parametros de hitches e doom_enabled, adicionando botoes condicionalmente
- [x] 2.6 Alterar `execute_player_roll` e chamadores em `cogs/rolling.py` para passar informacao de hitches e config de doom para PostRollView
- [x] 2.7 Adicionar testes para hitch action buttons: complicacao criada, PP concedido, step up de duplicata, doom adicionado

## 3. Doom Roll na PostRollView

- [x] 3.1 Adicionar `DoomRollButton` (reutilizar de `views/doom_views.py` ou criar variante) na PostRollView quando doom_pool habilitado
- [x] 3.2 Alterar PostRollView para receber flag doom_enabled e incluir botao condicionalmente
- [x] 3.3 Registrar DynamicItems de hitch e doom no `setup_hook` para persistencia apos restart
- [x] 3.4 Adicionar testes para doom roll via PostRollView

## 4. Botao Menu em toda View publica

- [x] 4.1 Criar `MenuButton` (DynamicItem persistente) em `views/common.py` que envia menu contextual ephemeral ao ser clicado
- [x] 4.2 Adicionar `MenuButton` a todas as Views publicas: PostRollView, PostDoomActionView, PostStateActionView, PostSceneView, PostCampaignView
- [x] 4.3 Excluir `MenuButton` da View gerada pelo proprio `/menu` para evitar redundancia
- [x] 4.4 Registrar `MenuButton` no `setup_hook`
- [x] 4.5 Adicionar testes para MenuButton: envia menu correto por contexto, nao aparece em /menu

## 5. Integracao e validacao

- [x] 5.1 Executar suite completa de testes e corrigir regressoes
- [x] 5.2 Verificar que PostRollView nao excede 5 botoes por ActionRow (distribuir em 2 rows se necessario)
- [x] 5.3 Verificar acessibilidade: todas as mensagens de confirmacao de hitch actions sao texto linear descritivo
