## 1. Bugfixes e correcoes de texto

- [x] 1.1 Corrigir todas as referencias a `/setup` para `/campaign setup` em campaign.py, state.py, rolling.py, scene.py e doom.py
- [x] 1.2 Converter parametro `confirm` em `/campaign end` de texto livre para `app_commands.Choice` com opcao "sim"
- [x] 1.3 Corrigir description do parametro `player` em `/asset add`: remover "Omitir para asset de cena", manter apenas "Jogador dono do asset (default: voce)"

## 2. Mensagens de erro em portugues

- [x] 2.1 Traduzir mensagens de erro em `dice.py` (parse_single_die, parse_dice_notation) para portugues
- [x] 2.2 Padronizar mensagem de "nenhuma campanha ativa" entre todos os cogs para referenciar `/campaign setup` de forma consistente
- [x] 2.3 Atualizar testes em test_dice.py para validar mensagens em portugues

## 3. Formato de rolagem total-first

- [x] 3.1 Reestruturar `format_roll_result` em formatter.py para formato "Total N (dX tirou Y, dZ tirou W). Effect die: dN."
- [x] 3.2 Adaptar formato para best_options: label primeiro, depois total, depois detalhe
- [x] 3.3 Adaptar formato para rolagem com difficulty: resultado (sucesso/falha) imediatamente apos total
- [x] 3.4 Atualizar testes de formatter para validar novo formato

## 4. Separadores no campaign/scene info

- [x] 4.1 Inserir separador "---" entre blocos de jogadores em `format_campaign_info` no formatter.py
- [x] 4.2 Atualizar testes de format_campaign_info para validar separadores

## 5. Feedback legivel no undo

- [x] 5.1 Criar mapa ACTION_LABELS em undo.py com templates narrativos por action_type
- [x] 5.2 Substituir loop key=value por lookup no mapa com fallback para formato tecnico
- [x] 5.3 Adicionar testes para feedback legivel do undo (templates conhecidos e fallback)

## 6. Help system

- [x] 6.1 Criar `cogs/help.py` com comando `/help` e parametro `topic` (Choice: geral, gm, jogador, rolagem)
- [x] 6.2 Escrever conteudo das 4 variantes de help como strings hardcoded no cog
- [x] 6.3 Registrar cog de help em bot.py
- [x] 6.4 Adicionar testes para o cog de help

## 7. Mensagens guiadas de lifecycle

- [x] 7.1 Adicionar bloco "Proximos passos" ao output de `/campaign setup` bem-sucedido em campaign.py
- [x] 7.2 Adicionar bloco de comandos de jogo ao output de `/scene start` bem-sucedido em scene.py
- [x] 7.3 Adicionar bloco de continuidade ao output de `/scene end` em scene.py
- [x] 7.4 Adicionar testes para mensagens guiadas nos tres pontos de transicao
