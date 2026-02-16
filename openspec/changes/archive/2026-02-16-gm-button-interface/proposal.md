## Why

Slash commands do Discord são inacessíveis para o GM (que usa screen reader). O overlay de slash commands congela o VoiceOver, e a configuração "Legacy Chat Input" (necessária para acessibilidade em outros contextos) quebra slash commands completamente. Prefix commands (m!roll) resolveriam parcialmente, mas não oferecem autocomplete nem validação de parâmetros. Discord UI components (buttons, select menus) são elementos HTML focáveis padrão, bem rotulados para screen readers segundo avaliação da American Foundation for the Blind. A solução é oferecer uma interface paralela via buttons e select menus para o GM, mantendo slash commands para os jogadores videntes.

## What Changes

- Adicionar Views com botões contextuais a toda resposta do bot, oferecendo as ações mais prováveis como próximo passo (ex: após scene start, botões para /roll, /stress add, /asset add).
- Implementar select menu chains para comandos que exigem múltiplos parâmetros (ex: stress add → selecionar jogador → selecionar tipo → selecionar dado), substituindo modals com campos de texto.
- Usar `persistent=True` em todas as Views para sobreviver ao timeout de 15 minutos e restarts do bot.
- Registrar todas as persistent views no `setup_hook` do bot.
- Manter slash commands intactos como interface primária para jogadores.

## Capabilities

### New Capabilities
- `gm-button-views`: Sistema de Views com botões contextuais e select menu chains que permite ao GM executar todas as operações do bot via componentes acessíveis, sem depender de slash commands.

### Modified Capabilities
- `accessibility`: O requirement "Toda funcionalidade via slash command direto" precisa ser relaxado. Slash commands continuam como interface completa para jogadores, mas o GM pode operar exclusivamente via buttons/selects. Botões deixam de ser "atalhos opcionais" e passam a ser interface primária alternativa.

## Impact

- `bot.py`: setup_hook precisa registrar persistent views.
- Todos os cogs que enviam respostas precisam anexar Views contextuais ao output.
- Novo módulo de views (provavelmente `views/` ou dentro de cada cog) com as definições de buttons e select menus.
- Intents: nenhuma mudança necessária (buttons não exigem Message Content Intent).
- Dependência: discord.py 2.x já suporta tudo (discord.ui.View, Button, Select).
- Custom IDs precisam ser estáveis e parseáveis para persistent views funcionarem após restart.
