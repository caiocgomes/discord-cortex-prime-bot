## Context

O fluxo atual de rolagem usa multi-select (DicePoolSelectView) seguido de outro multi-select para assets (AssetIncludeSelectView). Esse modelo tem dois problemas: o NVDA nao anuncia selecao em multi-select (bug nvaccess/nvda#18224), e o modelo mental de "selecionar tudo de uma vez" nao reflete como jogadores de Cortex Prime pensam sobre pool building (trait por trait, incrementalmente).

As chains de GM (stress/asset/complication/doom) tambem usam selects para dado e jogador, sofrendo do mesmo problema de acessibilidade.

## Goals / Non-Goals

**Goals:**
- Substituir multi-select de dice pool por pool builder interativo com botoes
- Permitir montagem incremental do pool (clique por clique) com feedback nos labels dos botoes
- Assets ativos do jogador aparecem como botoes toggle no mesmo painel
- Substituir selects de dado (d4-d12) por botoes nas chains de GM
- Substituir selects de jogador por botoes quando <= 5 jogadores
- Criar /menu como ponto de entrada acessivel

**Non-Goals:**
- Persistencia do pool builder (e efemero, morre com a view)
- Pool builder para /gmroll (GM continua usando slash command)
- Suporte a mais de 10 assets simultaneos (limite pratico de 2 ActionRows)
- Substituir slash commands existentes (botoes sao complementares)

## Decisions

### Decision 1: PoolBuilderView com estado em memoria

O PoolBuilderView mantem estado (`pool: list[int]`, `included_assets: set[int]`) em memoria na instancia da view. Cada clique de botao modifica o estado e chama `_rebuild()` que recria todos os botoes e faz `edit_message` com o conteudo e view atualizados.

**Alternativa considerada:** Codificar estado no custom_id dos botoes. Descartado porque o limite de 100 chars no custom_id nao comporta um pool arbitrario, e views efemeras nao precisam sobreviver restart.

### Decision 2: Labels dos botoes carregam estado

Em vez de depender do texto da mensagem (que o NVDA nao anuncia apos edit_message), o estado e codificado nos labels dos botoes:
- Dado com contagem: `+d8 (2)` indica 2x d8 no pool
- Asset incluido: `Sword d8 (no pool)` indica toggle ativo
- Botao de rolar: `Rolar 4 dados` indica tamanho total do pool

Quando o usuario navega com Tab entre os botoes, o NVDA le o label e anuncia o estado atual sem precisar navegar ao texto da mensagem.

### Decision 3: Dados adicionam, assets fazem toggle

Comportamento diferenciado por tipo de botao:
- **Dados (d4-d12):** cada clique adiciona +1 ao pool. Motivo: e comum querer 2d8 ou 3d6.
- **Assets:** toggle on/off. Motivo: cada asset so pode ser incluido uma vez.

### Decision 4: Helpers genericos em base.py

`add_die_buttons(view, callback)` e `add_player_options(view, players, callback, extra_buttons)` sao helpers reutilizados tanto no pool builder quanto nas chains de GM. Mesmo pattern do branch anterior.

### Decision 5: Botao "Remover ultimo" em vez de undo por tipo

Um unico botao "Remover ultimo" que remove o ultimo dado/asset adicionado ao pool. Mais simples que ter botoes de remocao por tipo de dado. O botao so aparece quando o pool nao esta vazio.

### Decision 6: Layout de ActionRows

```
Row 1: [+d4] [+d6] [+d8] [+d10] [+d12]     (5 botoes, 1 row fixo)
Row 2: [Asset1] [Asset2] ...                  (0-2 rows, dinamico)
Row 3: [Rolar N dados] [Limpar] [Rem. ultimo] (1 row de controles)
```

Maximo: 4 rows para ate 10 assets. Na pratica, jogadores raramente tem mais de 3 assets ativos.

### Decision 7: execute_player_roll() extraida

Logica duplicada entre DicePoolSelectView._execute_roll e AssetIncludeSelectView._execute_roll e extraida para funcao `execute_player_roll()` em rolling_views.py. Reutilizada pelo PoolBuilderView e potencialmente por outros fluxos.

## Risks / Trade-offs

**[NVDA nao anuncia edit_message automaticamente]** O usuario precisa navegar manualmente para verificar o estado apos cada clique. Mitigacao: estado nos labels dos botoes reduz essa necessidade. O amigo do usuario quer testar exatamente isso.

**[Limite de 25 componentes por mensagem]** Com 5 dados + 10 assets + 3 controles = 18 componentes, estamos dentro do limite. Mas se assets + complications + stress fossem todos botoes, ultrapassaria. Mitigacao: apenas assets do jogador aparecem no pool builder.

**[Pool vazio ao clicar Rolar]** Se o usuario clicar Rolar sem adicionar dados, responder com erro efemero sem fechar o pool builder.
