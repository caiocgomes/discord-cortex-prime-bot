## Requirements

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

### Requirement: Sem dependencia de emojis para informacao

O bot SHALL NOT usar emojis como unico veiculo de informacao. Emojis decorativos sao permitidos apenas se acompanhados de texto equivalente. Status (sucesso, falha, aviso) SHALL ser comunicado em palavras.

#### Scenario: Sucesso sem emoji obrigatorio

- **WHEN** bot indica sucesso numa rolagem
- **THEN** output diz "Sucesso, margem [N]." em texto, sem depender de checkmark visual.

### Requirement: Toda funcionalidade via slash command direto

Toda operacao do bot SHALL ser executavel via slash command com parametros OU via buttons/select menus. Slash commands continuam como interface completa. Buttons e select menus oferecem interface alternativa completa para operacoes de gameplay, permitindo uso do bot sem digitar slash commands.

#### Scenario: Rolagem completa sem interacao visual

- **WHEN** jogador executa `/roll dice:1d8 1d10 include:wrench difficulty:11`
- **THEN** bot executa rolagem completa e exibe resultado sem exigir cliques adicionais.

#### Scenario: Componentes visuais como interface alternativa

- **WHEN** bot apresenta botoes apos uma acao
- **THEN** cada botao inicia uma acao completa via callbacks, sem exigir slash commands.
- **AND** a mesma acao permanece disponivel via slash command correspondente.

#### Scenario: Operacao completa via botoes sem slash

- **WHEN** GM usa exclusivamente botoes e select menus durante uma sessao inteira
- **THEN** todas as operacoes de gameplay (scene, roll, stress, asset, complication, doom, undo) sao executaveis sem digitar nenhum slash command.

### Requirement: Autocomplete em parametros de comandos

Parametros que referenciam elementos existentes (nomes de jogadores, assets, tipos de stress, crisis pools) SHALL usar autocomplete do Discord para permitir selecao via teclado.

#### Scenario: Autocomplete de nome de jogador

- **WHEN** GM digita `/stress add player:` e comeca a digitar "Al"
- **THEN** Discord sugere "Alice" via autocomplete, selecionavel por teclado.

#### Scenario: Autocomplete de asset

- **WHEN** Alice digita `/roll include:` e comeca a digitar "wr"
- **THEN** Discord sugere "Big Wrench" via autocomplete.

### Requirement: Feedback textual para toda acao

Toda acao executada SHALL receber confirmacao em texto descrevendo o que foi feito. O feedback SHALL ser suficiente para um usuario de screen reader entender o estado resultante sem consultar `/campaign info`.

#### Scenario: Confirmacao de adicao de stress

- **WHEN** GM executa `/stress add player:Alice type:Physical die:d8`
- **THEN** bot responde "Stress Physical d8 adicionado a Alice. Alice agora tem: Physical d8, Mental d6. PP 3."

#### Scenario: Confirmacao de fim de cena

- **WHEN** GM executa `/scene end bridge:yes`
- **THEN** bot descreve em texto cada elemento removido, cada step down de stress por jogador, e o estado persistente.

#### Scenario: Feedback legivel no undo

- **WHEN** usuario executa `/undo` e a acao desfeita foi adicao de asset
- **THEN** bot responde com texto narrativo como "Desfeito: Asset 'Big Wrench' d8 adicionado a Alice." em vez de formato tecnico.

#### Scenario: Feedback legivel no undo com fallback

- **WHEN** usuario executa `/undo` e o action_type nao tem template legivel mapeado
- **THEN** bot usa o formato tecnico atual como fallback, sem erro.

### Requirement: Mensagens de validacao de dados em portugues

As funcoes de validacao de dados em dice.py SHALL retornar mensagens de erro em portugues. A mudanca cobre parse_single_die e parse_dice_notation.

#### Scenario: Dado invalido

- **WHEN** usuario fornece "d7" como dado
- **THEN** mensagem de erro SHALL ser "d7 nao e um dado Cortex valido. Use d4, d6, d8, d10 ou d12."

#### Scenario: Notacao invalida

- **WHEN** usuario fornece "abc" como notacao de dado
- **THEN** mensagem de erro SHALL ser "Notacao de dado invalida: abc"

### Requirement: Mensagens de erro de campanha em portugues consistente

Todas as mensagens de erro que referenciam setup SHALL usar o caminho correto `/campaign setup` em vez de `/setup`. Cogs que verificam existencia de campanha ativa SHALL usar mensagem padronizada.

#### Scenario: Referencia correta ao setup

- **WHEN** usuario executa comando de jogo sem campanha ativa
- **THEN** mensagem de erro referencia `/campaign setup` (nao `/setup`).
