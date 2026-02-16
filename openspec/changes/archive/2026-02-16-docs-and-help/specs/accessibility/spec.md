## MODIFIED Requirements

### Requirement: Output em texto linear estruturado

Todas as respostas do bot SHALL ser formatadas como texto linear, sem box art, sem ASCII art, sem layout espacial que dependa de posicionamento visual. Informacoes SHALL ser apresentadas em frases completas ou listas simples separadas por quebras de linha.

#### Scenario: Resultado de rolagem acessivel

- **WHEN** bot exibe resultado de rolagem
- **THEN** output segue formato total-first: "Total [N] ([die_size] tirou [valor], [die_size] tirou [valor]). Effect die: [die_size]."

#### Scenario: Resultado de rolagem com best mode

- **WHEN** bot exibe resultado de rolagem com best_options habilitado
- **THEN** output segue formato: "[label]: [total] ([die_size] tirou [valor], [die_size] tirou [valor]). Effect die: [die_size]." para cada opcao.

#### Scenario: Resultado de rolagem com dificuldade

- **WHEN** bot exibe resultado de rolagem com difficulty definido
- **THEN** output coloca resultado (sucesso/falha) imediatamente apos o total: "Total [N]. Sucesso, margem [M] ([detalhe dos dados]). Effect die: [die_size]." ou "Total [N]. Falha, faltou [M] ([detalhe dos dados])."

#### Scenario: Info da campanha acessivel

- **WHEN** bot exibe `/campaign info`
- **THEN** output lista cada jogador com seus dados, separado do proximo jogador por "---". Formato por jogador: "[nome]: [stress/assets/complications em texto]. PP [N], XP [N]."

#### Scenario: Info da cena acessivel

- **WHEN** bot exibe `/scene info`
- **THEN** output usa os mesmos separadores "---" entre blocos de jogadores.

### Requirement: Feedback textual para toda acao

Toda acao executada SHALL receber confirmacao em texto descrevendo o que foi feito. O feedback SHALL ser suficiente para um usuario de screen reader entender o estado resultante sem consultar `/campaign info`.

#### Scenario: Confirmacao de adicao de stress

- **WHEN** GM executa `/stress add player:Alice type:Physical die:d8`
- **THEN** bot responde "Stress Physical d8 adicionado a Alice. Alice agora tem: Physical d8, Mental d6. PP 3."

#### Scenario: Feedback legivel no undo

- **WHEN** usuario executa `/undo` e a acao desfeita foi adicao de asset
- **THEN** bot responde com texto narrativo como "Desfeito: Asset 'Big Wrench' d8 adicionado a Alice." em vez de formato tecnico "action_type=add_asset, key=Big Wrench, value=d8".

#### Scenario: Feedback legivel no undo com fallback

- **WHEN** usuario executa `/undo` e o action_type nao tem template legivel mapeado
- **THEN** bot usa o formato tecnico atual como fallback, sem erro.

## ADDED Requirements

### Requirement: Mensagens de validacao de dados em portugues

As funcoes de validacao de dados em dice.py SHALL retornar mensagens de erro em portugues. A mudanca cobre parse_single_die e parse_dice_notation.

#### Scenario: Dado invalido

- **WHEN** usuario fornece "d7" como dado
- **THEN** mensagem de erro SHALL ser "d7 nao e um dado Cortex valido. Use d4, d6, d8, d10 ou d12."

#### Scenario: Notacao invalida

- **WHEN** usuario fornece "abc" como notacao de dado
- **THEN** mensagem de erro SHALL ser "Notacao de dado invalida: abc"

#### Scenario: Quantidade invalida

- **WHEN** usuario fornece "0d8" como notacao de dado
- **THEN** mensagem de erro SHALL estar em portugues, indicando que a quantidade precisa ser pelo menos 1.

### Requirement: Mensagens de erro de campanha em portugues consistente

Todas as mensagens de erro que referenciam setup SHALL usar o caminho correto `/campaign setup` em vez de `/setup`. Cogs que verificam existencia de campanha ativa SHALL usar mensagem padronizada.

#### Scenario: Referencia correta ao setup

- **WHEN** usuario executa comando de jogo sem campanha ativa
- **THEN** mensagem de erro referencia `/campaign setup` (nao `/setup`).

#### Scenario: Consistencia entre cogs

- **WHEN** qualquer cog (campaign, scene, state, rolling, doom) detecta ausencia de campanha
- **THEN** todas usam a mesma mensagem padrao referenciando `/campaign setup`.
