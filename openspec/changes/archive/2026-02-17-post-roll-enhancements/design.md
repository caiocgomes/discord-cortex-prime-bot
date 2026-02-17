## Context

O bot já tem o fluxo completo de rolagem (pool builder, best mode, hitches, PostRollView) e o sistema de botões contextuais (gm-button-views). O doom pool funciona via slash commands e botões dedicados. O `/menu` existe como comando avulso. O GM primário é cego e usa screen reader, então toda informação precisa estar acessível em texto linear e toda funcionalidade precisa ser alcançável sem navegar entre mensagens.

Problema central: o fluxo pós-rolagem está incompleto. O jogador não vê todos os dados para decidir sobre PP, o GM precisa sair da mensagem de roll para resolver hitches ou rolar doom, e os botões de ação desaparecem entre mensagens.

## Goals / Non-Goals

**Goals:**
- Jogador vê todos os resultados individuais para decidir gasto de PP
- GM resolve hitches (complicação ou doom) sem sair da mensagem de rolagem
- GM rola doom pool direto da PostRollView
- Botões de navegação persistem em toda saída do bot

**Non-Goals:**
- Não alterar a mecânica de cálculo de best options
- Não adicionar rolagem automática de doom como oposição (GM decide quando rolar)
- Não alterar o fluxo do pool builder em si
- Não implementar gasto de PP via botão para somar dado extra ao resultado já rolado (isso seria uma feature futura)

## Decisions

### 1. Resultados individuais antes das best options

Inserir `_format_dice_detail(results, hitches)` como linha separada no `format_roll_result`, antes do bloco de best_options. A linha já é computada (variável `detail` na linha 54) mas não é usada quando best_options existe.

Alternativa considerada: mostrar os dados apenas dentro das best options com destaque. Rejeitado porque o jogador precisa ver dados que NÃO estão em nenhuma opção (são exatamente os candidatos para gasto de PP).

### 2. Hitch actions como botões condicionais na PostRollView

PostRollView recebe informação sobre hitches (quantidade e tamanho). Quando há hitches, dois botões adicionais aparecem:
- "Criar complicação" (DynamicItem, GM-only): abre chain de seleção de jogador alvo, depois pede nome da complicação via modal, cria complicação d6 e dá 1 PP ao jogador alvo
- "+Doom" (DynamicItem, GM-only): adiciona d6 ao doom pool diretamente

O tamanho da complicação é sempre d6 (regra do Cortex Prime para hitches). Se houver múltiplos hitches, o GM pode clicar múltiplas vezes ou usar step up depois. A ação de dar PP ao jogador que sofreu o hitch é automática.

Alternativa considerada: um único botão "Resolver hitch" que abre submenu com as duas opções. Rejeitado por adicionar um clique extra desnecessário.

### 3. Doom Roll na PostRollView

PostRollView ganha botão "Doom Roll" quando `doom_pool` está habilitado na config da campanha. O botão reutiliza a lógica existente do `DoomRollButton` (rola todo o pool, mostra best options, sugere dificuldade). Resultado aparece como followup na mesma thread.

O botão é DynamicItem persistente com campaign_id no custom_id, reaproveitando o pattern existente.

### 4. Menu contextual em toda saída do bot

Em vez de duplicar botões de menu em cada View individual, a abordagem é: toda View que aparece como resposta pública do bot inclui um botão "Menu" persistente. Clicar nesse botão envia o menu completo como mensagem ephemeral.

Alternativa considerada: anexar todos os botões do menu em toda mensagem. Rejeitado porque o limite do Discord é 5 ActionRows (25 botões), e PostRollView com hitches + doom + menu já estaria no limite. Um único botão "Menu" resolve sem estourar o layout.

Alternativa considerada: editar toda mensagem de resposta para incluir a MenuView completa. Rejeitado pela mesma razão de espaço.

### 5. Fluxo de criação de complicação via hitch

```
GM clica "Criar complicação"
  → View ephemeral: botões com jogadores da campanha (ou select se > 5)
    → GM seleciona jogador
      → Modal: campo de texto para nome da complicação
        → Bot cria complicação d6 no jogador + dá 1 PP ao jogador + loga ação
          → Mensagem pública confirmando
```

O modal (discord.ui.Modal) é a melhor opção para input de texto porque não exige mensagem intermediária e funciona bem com screen readers. O state_manager já tem métodos para criar complicação e atualizar PP; a transação deve ser atômica (uma única action_log entry ou duas entries sequenciais para permitir undo granular).

Decisão sobre undo: duas entries separadas (uma para complicação, uma para PP). Assim o GM pode desfazer individualmente se necessário.

## Risks / Trade-offs

**PostRollView ficando complexa**: Com Roll + Undo + Criar complicação + +Doom + Doom Roll + Menu, são 6 botões. Dentro do limite de 1 ActionRow (5 por row), mas precisa de 2 rows. → Mitigação: distribuir em 2 rows (ações de jogo na row 0, ações de resolução na row 1).

**Múltiplos hitches**: Se a rolagem produziu 3 hitches, o GM pode querer criar 3 complicações ou adicionar 3 dados ao doom. O botão aparece uma vez e o GM clica múltiplas vezes. → A PostRollView precisa persistir (timeout=None) para permitir múltiplos cliques. Cada clique abre uma nova chain efêmera.

**Menu button em mensagens existentes**: Views já criadas antes desta mudança não terão o botão Menu. Isso é aceitável; o `/menu` continua existindo como fallback.
