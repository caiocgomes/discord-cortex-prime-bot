# Cortex Prime: Extração de Regras Mecânicas para Bot Discord

Fonte: Cortex Prime Game Handbook (256 páginas). Extraído e filtrado para regras mecanicamente implementáveis em um bot de RPG online. Referências de página indicadas como (p.XX).

---

# Parte 1: Fundamentos do Sistema

## Dados e Ratings (p.16)

Cortex Prime usa cinco tipos de dados: d4, d6, d8, d10 e d12. Cada trait tem um die rating associado. A escala de poder segue d4 < d6 < d8 < d10 < d12.

**Stepping up** um dado troca pelo próximo maior (d4 → d6 → d8 → d10 → d12). **Stepping down** troca pelo próximo menor. Step down de d4 elimina o dado. Step up além de d12 resulta em takeout automático ou, em certas situações, um segundo effect die (p.21). Stepping pode ocorrer por mais de um step de uma vez.

## Dice Pool: Montagem e Resolução (p.17)

O jogador monta um dice pool selecionando um dado de cada trait set relevante, mais dados de assets, complications (no pool da oposição), plot points gastos e SFX. Pools típicos têm 3-8 dados, sem máximo.

**Roll and Keep:** o jogador **escolhe dois resultados para somar como total**, depois **escolhe um terceiro dado como effect die**. Pode escolher quaisquer dois dados para o total, não necessariamente os dois maiores. Se sobrar apenas um dado, ele é o total. Se não sobrar dado para effect die, o default é d4.

Todas as rolagens são feitas abertamente.

## Hitches, Botches e Opportunities (p.17, 28, 37)

**Hitch:** dado que rola 1. Não conta para total nem pode ser effect die. O GM pode dar ao jogador um PP para criar uma complication d6. Hitches adicionais na mesma rolagem fazem step up da complication sem custo extra de PP.

**Botch:** todos os dados saem 1. Total é zero. O GM cria uma complication d6 gratuita (sem dar PP) e faz step up uma vez por hitch além do primeiro.

**Opportunity:** quando o GM rola 1. O jogador pode gastar um PP para step down uma complication existente ou step up um asset existente. Múltiplas opportunities permitem múltiplos steps. Custa um PP por complication/asset afetado.

Dados rerolados podem substituir hitches que ainda não foram gastos em outro efeito.

---

# Parte 2: Resolução (Capítulo 1, pp.18-25)

## Tests (p.18)

O GM monta um pool de oposição e rola primeiro, somando dois dados para definir a **dificuldade**. O jogador rola e precisa **superar estritamente** essa dificuldade. Empate conta como falha.

Dados de dificuldade base por severidade:

| Dificuldade | Dados |
|---|---|
| Muito Fácil | d4 d4 |
| Fácil | d6 d6 |
| Desafiador | d8 d8 |
| Difícil | d10 d10 |
| Muito Difícil | d12 d12 |

O GM pode adicionar dados ao pool de oposição baseado em traits de GMC, locação ou cena. Na dúvida, adicionar d6s.

## Contests (pp.19-20)

Iniciado por um jogador, que rola primeiro. Se a oposição não contestar após ver a rolagem, sucesso automático. Se a oposição superar o total do iniciador, o iniciador pode **dar in** (definindo a falha nos próprios termos, ganhando um PP, mas sem poder reiniciar contra o mesmo oponente) ou rolar novamente.

Contests vão e voltam até um lado dar in ou falhar em superar o total. O perdedor recebe uma complication. Em cenas high stakes, pode ser taken out.

Dar in durante um contest (após ter rolado pelo menos uma vez) ganha um PP. Não rolar desde o início não ganha PP.

## Heroic Success (p.20)

Se o total supera a dificuldade por 5+, é um **heroic success**. O effect die faz step up uma vez para cada 5 pontos de diferença.

## Effect Dice (pp.20-21)

Escolhido dos dados restantes após selecionar os dois para o total. Apenas o **tamanho do dado** importa, não o resultado rolado. Determina o tamanho de assets, complications ou stress criados.

**Dados inelegíveis:** hitch (rolou 1) não pode ser effect die. Dados adicionados ao total via PP também não. Se nenhum dado elegível restar, default é d4.

Se um SFX faz step up do effect die além de d12: ou é takeout automático, ou outro dado do pool vira um segundo effect die. Gastar PP permite manter um effect die extra.

## Effect Dice em Contests (pp.21-22)

**High stakes:** o vencedor compara seu effect die com o do perdedor. Se o do vencedor for **estritamente maior**, o perdedor é **taken out**. Se igual ou menor, ou se o perdedor gastar PP, recebe complication igual ao effect die do vencedor.

**Non-high-stakes:** o perdedor recebe complication igual ao effect die do vencedor. Se o effect die do perdedor for igual ou maior que o do vencedor, o effect die do vencedor faz **step down** antes de ser aplicado.

## Being Taken Out (p.22)

Personagem taken out não faz mais tests/contests na cena. Complication stepped up além de d12 automaticamente faz taken out. Pode retornar à cena via outros personagens, voltando com pelo menos complication d6.

**Stay in the Fight:** gastar PP para receber complication em vez de ser taken out (tamanho = effect die da oposição). O mod de stress substitui essa regra.

## Interferir em Contest (p.23)

Custa 1 PP após ambos os lados terem rolado pelo menos uma vez. O interferente rola: se falhar, recebe complication/stress do vencedor. Se superar, o contest para. Se ambos os lados originais quiserem continuar, cada um dá PP ao interferente e rola novamente.

## Contests com Múltiplos Personagens (p.23)

Um jogador inicia; outros entram um de cada vez. O maior total vence. Quem ficar e falhar recebe complication. Pode dar in normalmente.

---

## Mods de Tests e Contests (pp.24-25)

### Action-Based Resolution (p.24)

Tests/contests substituídos por **action/reaction**. O ator declara ação e rola. O alvo reage com sua própria rolagem ou o GM define difficulty dice. Empate favorece o ator (a reação precisa **exceder** o total da ação).

### Add All the Dice (p.25)

Todos os dados do pool são somados para o total. Hitches ainda aplicam. Sem effect die disponível. Use com No Effect Dice ou Reroll for Effect.

### No Effect Dice (p.25)

Effect dice eliminados. Pass/fail simples. Assets/complications gerados como d6 (stepped up em heroic successes).

### Reroll for Effect (p.25)

A rolagem original não gera effect die. O jogador rerola o pool inteiro e pega o maior dado como effect die. Modificações de SFX aplicam à nova rolagem.

### Static Difficulty (p.25)

Tests usam target number fixo: Muito Fácil 3, Fácil 7, Desafiador 11, Difícil 15, Muito Difícil 19. Complications do PC são roladas e adicionadas à dificuldade estática.

---

# Parte 3: Traits e Trait Sets (Capítulos 1-2)

## Regra Geral de Traits (p.26)

Cada trait tem die rating (d4-d12). Organizam-se em trait sets. Regra central: **apenas um trait de cada trait set** pode entrar no pool sem custo extra. Incluir segundo trait do mesmo set custa PP.

Todo jogo precisa de pelo menos **dois prime sets** mais distinctions. Prime sets fornecem dados obrigatórios para todo test/contest.

## Distinctions (p.50)

Todo personagem tem três distinctions (background, personalidade, papel narrativo). Sempre rated d8. Cada distinction tem o **Hinder SFX** de graça: "Ganhe um PP ao trocar o d8 dessa distinction por d4."

SFX adicionais podem ser travados/destravados via growth/XP. Mod de rating variável: d4-d12, com SFX destravados em d4, d8 e d12.

**Highlight traits (p.50):** mod onde cada distinction inclui dois highlight traits (geralmente skills) que fazem step up durante criação. Se um highlight aparece em duas distinctions: d8; em três: d10.

## Affiliations (p.48)

Refletem desempenho em contextos específicos. Set padrão: Solo, Buddy, Team. Ratings: d6/d8/d10.

## Attributes (p.49)

Capacidade bruta. Set clássico: Agility, Alertness, Intelligence, Strength, Vitality, Willpower. Alternativa: Physical, Mental, Social. Rating d4-d12, default d8.

## Skills (p.57-58)

Treinamento e experiência. Enquadradas como verbos: Craft, Drive, Fight, Fix, Fly, Focus, Influence, Know, Labor, Move, Notice, Operate, Perform, Shoot, Sneak, Survive, Throw, Treat, Trick. Rating: d4 (untrained) a d12 (grandmaster).

## Specialties (p.59)

Foco estreito dentro de uma skill. Confere bonus d6 na área específica. Aplica quando o assunto se sobrepõe, independente da skill rolada.

**Multi-level specialties mod:** d6 (Trained), d8 ou d6d6 (Expert), d10 ou d8d8 (Master), d12 ou d10d10 (Grandmaster).

**No Skills, Just Specialties mod:** specialties substituem skills inteiramente, rated d8-d12.

**Skill Pyramid mod:** para ter d10 skill, precisa de pelo menos duas d8 e três d6.

## Roles (p.58)

Substituem skills como grupos temáticos. 3-6 roles com arrays fixos:

- Três roles: d10, d8, d4
- Quatro roles: d10, d8, d6, d4
- Cinco roles: d10, d8, d6, d6, d4
- Seis roles: d10, d8, d6, d6, d6, d4

## Values (p.60)

Princípios/valores do personagem. Rating d4-d12 com **fixed total**: step up um obriga step down de outro. Não podem ir abaixo de d4 ou acima de d12.

## Relationships (p.55)

Intensidade de conexão com outro personagem/grupo. Rating d4 (sem sentimento) a d12 (ninguém importa mais). Contribui die ao pool quando o test/contest envolve o personagem vinculado.

Criar d6 relationship em jogo: gastar PP (como asset temporário). Dura a sessão; pode ser permanente via growth.

## Reputations (p.55)

Mod de relationships. Standing com grupo/organização. Funciona como relationship mas pode ser afetado por ações em jogo.

## Resources (p.56)

Quatro tipos: Extras, Locations, Organizations, Props. Representados por múltiplos dados do mesmo tamanho (ex: d6d6d6). Dados commitados antes do pool, rolados separadamente. Se múltiplos resource dice gastos, apenas o maior é aplicado ao total. Dados gastos são expendidos até recovery.

## Powers e Power Sets (pp.51-52)

Power = trait representando habilidade sobre-humana. Rating d6-d12. Um **power set** agrupa powers tematicamente com pelo menos um SFX e um limit. Cada power set conta como trait set próprio. Personagem com dois power sets pode incluir um power de cada no pool sem custo extra.

Power set shut down = não contribui dados até recovery condition ser atendida.

## Abilities (p.54)

Mod de power sets. Ability = trait rated com SFX próprios (sem Hinder). Categorias de efeito: Attack, Sensory, Movement, Control, Defense, Enhancement. Descritores customizáveis. Um SFX grátis na criação; destravam em d8 e d12.

**Powers e Abilities são mutuamente exclusivos.** O jogo usa um ou outro.

## Signature Assets (pp.64-65)

Armas/gear/companheiros icônicos. Permanentes, rated d6+. Não compartilháveis. Podem ter SFX (sem default). Recovery entre sessões ou PP no início da próxima cena.

## Trait Statements (p.65)

Frase clarificando um trait. **Challenging:** agir contrário ao statement triplica o die do trait naquela rolagem. Depois, o trait faz step down. No fim da sessão: reescrever o statement (restaura rating) ou manter (die reduzido permanece).

## Talents (p.66)

Trait sem die rating, com texto descritivo e SFX (activation + effect). Começam com 2, mais via growth.

---

# Parte 4: Plot Points (pp.27-29)

## Economia Básica

Todo jogador começa cada sessão com pelo menos 1 PP. PPs não gastos persistem entre sessões. PPs ganhos numa rolagem não podem ser gastos até a rolagem ser totalmente resolvida.

## GM e Plot Points (p.27)

**Bank:** 1 PP por jogador no início. Compartilhado por todos GMCs. Usado para: evitar takeout de GMCs, ativar SFX de GMCs. Quando gasto, vai para o pile (não para jogador afetado).

**Pile:** supply ilimitada. GM usa para dar PPs aos jogadores (ativando hitches, SFX). Quando jogadores/GM gastam PPs, retornam ao pile.

## Ganhar PPs como Jogador (p.28)

- **Complications de hitches:** GM dá PP do pile para criar d6 complication. Hitches extras fazem step up sem custo adicional. Múltiplas complications separadas custam PP cada. Botch: complication grátis + step up por hitch.
- **d4 voluntário no pool:** incluir d4 complication/stress voluntariamente no pool ganha PP (mesmo mecanismo do Hinder).
- **Dar in:** após rolar pelo menos uma vez num contest, ganha PP.
- **Roleplay:** GM pode premiar momentos marcantes.
- **SFX:** alguns SFX (incluindo Hinder) ganham PP.

## Gastar PPs como Jogador (pp.28-29)

- **Ativar SFX:** efeito dura uma rolagem.
- **Adicionar dados (antes de rolar):** PP para incluir dado adicional de trait set já representado. Requer justificativa narrativa.
- **Incluir mais resultados (após rolar):** PP por dado adicional somado ao total (além dos dois iniciais). Esses dados não podem ser effect dice.
- **Ativar Opportunity:** quando GM rola 1, gastar PP para step down complication ou step up asset. Múltiplas opportunities = múltiplos steps. Um PP por complication/asset.
- **Criar asset temporário:** 1 PP = d6 asset (cena). 2 PP total = resta da sessão. PP adicional = "open" para qualquer personagem.
- **Criar relationship:** PP para d6 relationship (sessão).
- **Manter effect die extra:** PP para segundo effect die dos dados restantes.
- **Rolar hero die:** PP para rolar hero die banked e somar ao total. Pode ser após oposição rolar, antes do resultado.
- **Compartilhar asset:** PP para tornar asset pessoal "open".
- **Interferir em contest:** PP para entrar.
- **Stay in the fight:** PP para receber complication em vez de taken out.

## Gastar PPs como GM (p.29)

- **Incluir mais resultados:** do bank, PP por dado adicional no total de GMC.
- **Ativar SFX:** do bank, PP para SFX de GMC.
- **Evitar takeout:** do bank, PP para GMC tomar complication em vez de taken out.

## Plot Point Mods (p.29)

**Starting PP Variants:** mais de 1 PP; rolar d4; rolar prime set e comparar totais (maior 3 PP, menor 1 PP, resto 2 PP).

**No Bank:** GM sem bank privado. Quando GM gasta PP em rolagem de GMC, PP vai direto ao jogador-alvo. GMC major não ganha PP usando distinction como d4; em vez disso, GM banca d6 para uso futuro daquele GMC.

---

# Parte 5: Hero Dice e Doom Pool (pp.30-33)

## Hero Dice (pp.30-31)

### Ganhar

Em heroic success, bancar um dado igual ao **maior dado rolado no pool da oposição**. Isso não anula o efeito padrão de heroic success (step up do effect die); ambos se aplicam. Se regra de "um por tamanho": pode step down para o próximo tamanho disponível.

### Usar

Gastar PP para rolar hero die banked e somar ao total. Pode ser após oposição rolar, antes do resultado. Hero die é consumido.

Se hero die rola 1: GM pode introduzir complication, mas jogador pode escolher tomar o hero die de volta (sem somar ao total) em vez de aceitar PP da complication. PP gasto para ativar é perdido de qualquer forma.

Hero dice não persistem entre rolagens num contest.

### GM e Hero Dice

GM não usa hero dice. Quando GM rola 5+ acima do total do jogador, remove um hero die do PC (igual ou menor que o maior dado rolado pelo GM).

### Mods de Hero Dice

**Hero Dice as PP:** hero dice podem ser incluídos no pool antes de rolar (sem custo PP, apagado da sheet). Podem substituir PP em qualquer situação aplicável.

**Hero Dice as Effect Dice:** gastar PP para substituir effect die baixo por hero die banked. Heroic success NÃO faz step up de hero die usado como effect die.

## Doom Pool (pp.32-33)

### Setup

Substitui bank de PPs do GM e difficulty dice. Começa cada sessão com mínimo d6 d6. Escala global: 3-4 dados. Breakpoints de campanha: dados iniciais podem ser d8 ou d10.

### Definir Dificuldade

GM rola alguns ou todos os dados do doom pool, escolhe dois para total. Pode gastar um dado adicional (não usado no total) adicionando seu resultado ao total; esse dado é **removido** do pool. Os demais ficam.

### Adicionar a Pools de GMC

GM pode gastar dado do doom pool para adicionar ao pool de um GMC (antes de rolar). Dado removido permanentemente.

### Doom Dice como PP Equivalente

d6 do doom pool = 1 PP. Se só restam dados maiores, gasta o próximo disponível.

### Crescimento do Doom Pool

Hitches dos jogadores: em vez de criar complication, GM adiciona dado ao doom pool do **mesmo tamanho do dado que rolou o hitch** e dá PP ao jogador. Alternativa: usar dado menor para step up dado igual ou maior já existente no doom pool.

### Efeitos de Cena do Doom Pool (pp.32-33)

- **Criar complication/asset/scene distinction:** gastar doom die; elemento criado = tamanho do dado gasto. Scene distinction requer pelo menos d8.
- **Interromper action order:** gastar doom die ≥ maior trait de combate/sentidos do PC cuja vez é próxima.
- **Adicionar extra:** gastar doom die para criar extra com single trait daquele tamanho.
- **Introduzir GMC minor/major:** gastar doom die ≥ trait mais alto do GMC.
- **Dividir o grupo:** gastar d10 ou d12.
- **Encerrar cena imediatamente:** gastar d12 d12.

### Limited Doom Pool (p.33)

Dificuldade determinada normalmente. Doom dice gastos para adicionar dados à dificuldade ou incluir mais dados no total após rolar.

### Crisis Pools (p.33)

Cada problema localizado tem pool próprio que funciona como doom pool menor. PCs podem eliminar crisis dice fazendo test contra o crisis pool. Se superar dificuldade e effect die for pelo menos um step maior que o crisis die: remove o crisis die. Se igual ou menor: step down do crisis die. Crisis pool zerado = problema resolvido.

---

# Parte 6: Assets e Complications (pp.34-43)

## Assets (pp.34-35)

**PP-created:** 1 PP = d6 asset (cena). PP adicional = sessão. PP adicional = "open". Múltiplos assets aplicáveis entram no pool sem custo extra (PP já foi gasto na criação).

**Step up:** via GM opportunities ou SFX. Máximo d12.

**Test-created:** jogador declara ação, monta pool, GM define dificuldade (tipicamente d6 d6). O **effect die** do test vira o rating do asset. GM pode definir **cap** no tamanho do asset configurando os difficulty dice. Falha = sem asset. PP para bancar, dar a outro, ou estender duração.

**Stunts:** assets criados por SFX, começam em d8.

**Freeform:** GM pode permitir test bem-sucedido criar d6 asset grátis.

**Clues:** usar percepção/sentidos cria asset. Dificuldade padrão d6 d6.

## Complications (pp.36-38)

**Usar:** vão no pool da **oposição** quando relevantes. Sem custo. Sem limite de quantidade. Uma complication por hindrance específico (sem "double jeopardy"; step up da existente).

**Criar de hitches:** GM dá PP e cria d6 complication. Hitches adicionais fazem step up. GM pode alternativamente step up complication existente.

**De contests:** die rating = effect die do vencedor. Se não de dado, começa d6.

**De botch:** complication grátis, d6 + step up por hitch além do primeiro.

**Step up existente:** se nova complication seria ≤ existente, existente faz step up. Além de d12 = taken out.

**Complication d4 (p.38):** quando aplica, vai no pool **do próprio personagem** (não da oposição), ganha PP. Depois da rolagem: eliminada, exceto se jogador rolou hitch (GM pode step up para d6+).

### Recovering Complications (pp.37-38)

Test vs pool de complication die + dificuldade base d8 d8. Outcomes:

1. **Supera dificuldade, effect die > complication:** eliminada.
2. **Supera dificuldade, effect die ≤ complication:** step down. Não pode tentar de novo até passar tempo.
3. **Supera dificuldade com hitch:** GM pode dar PP e introduzir nova complication relacionada.
4. **Falha:** complication inalterada.
5. **Falha com hitches:** complication faz step up por hitch.

---

## Stress (pp.39-40)

Substitui complications para dano pessoal. Complications continuam para hindrances externas.

### Infligir Stress

Se PC não tem stress ou tem stress menor que incoming: novo stress die substitui. Se PC já tem stress ≥ incoming: stress existente faz step up.

### Stress d4

Vai no pool do próprio jogador, ganha PP. Após rolagem: eliminado, ou step up se hitch.

### Oposição e Stress

Apenas **um tipo de stress** no pool de oposição por vez, exceto se GM pagar PP para adicionar mais.

### Tipos de Stress (p.40)

Configurações comuns: Physical/Mental/Social; ou Afraid/Angry/Exhausted/Injured/Insecure; ou track único.

### Recovering Stress (p.40)

Step down automático de um em cenas de descanso/downtime/transição. Sem recovery entre action scenes consecutivas. Recovery ativo: mesmo procedimento de complications (d8+d8 + stress die).

### Stressed Out (p.40)

Stress stepped up além de d12 = taken out. Por default, PP não previne. Enquanto stressed out, tratado como d12 stress para incoming adicional.

### Pushing Stress (p.40)

Gastar PP para adicionar stress die ao **próprio** pool (em vez do da oposição). Após resolver: stress faz step up. Pode causar stressed out.

## Trauma (p.41)

Quando stress faz step up além de d12: personagem ganha d6 **trauma** do mesmo tipo. Enquanto stressed out com trauma, stress adicional vai direto para trauma. Trauma além de d12 = remoção permanente.

**Recovery de trauma:** test vs d8+d8 + trauma die.

- **Supera:** trauma step down.
- **Supera com hitch:** trauma step down, mas GM pode introduzir complication ou infligir stress de tipo diferente.
- **Falha:** inalterado. Não pode tentar até passar tempo.
- **Falha com hitches:** trauma step up por hitch. Se além de d12: remoção permanente.

Trauma nunca faz auto-recovery.

## Shaken e Stricken (p.42)

Stress aplicado diretamente a traits específicos. Oponente escolhe qual trait recebe stress.

**Shaken:** stress no trait excede o die rating do trait. Personagem só pode manter um dado para total.

**Stricken:** já shaken e segundo trait também ficaria shaken. Taken out. Stress além de d12 em qualquer trait também causa stricken.

## Life Points (p.43)

Life points = soma de dois die ratings de traits. Dano = diferença entre o necessário e o rolado.

**Ablative:** dano subtraído de life points. A 0 ou menos: taken out. PP mantém vivo; cada hit adicional requer PP. Negativo igual ao score original = morte.

**Threshold:** dano dividido em wounds e stun. Se wounds + stun > score: inconsciente. Se wounds > score: morte.

**Recovery:** test vs d6 d6 + complications. Diferença = life points recuperados.

---

# Parte 7: Cenas e Conflito (Capítulo 3, pp.88-112)

## Estrutura de Cenas (p.88)

Cena é a unidade primária de jogo. Subdivide-se em **beats** (unidade dramática mínima = uma ação/test). GM enquadra e encerra cenas.

## Tipos de Cenas (p.89)

| Tipo | Mecânica |
|---|---|
| Opening | Sem tests/contests por default |
| Action | Conflito, tests/contests, SFX, action order |
| Bridge | Downtime: recovery de complications/stress (step down automático), criar/upgrade assets |
| Exploration | Tests contra ambiente/dificuldade abstrata, clue assets |
| Flashback | Cena no passado para criar asset; test simples preferível a contest |
| Tag | Fim de sessão: trait statements, milestones, growth |

## Action Order / Handoff Initiative (p.98)

**Actions e Reactions:** tests/contests substituídos por ação (ofensiva) e reação (defensiva). Empate favorece o ator.

**Quem começa:** GM decide action lead pela ficção.

**Progressão de turnos:** todos (PC e GMC) têm um turno por round. Após agir, escolhe o próximo personagem. O último a agir escolhe action lead do próximo round (pode se auto-nomear).

### Taking Initiative Mod (p.99)

Quatro variantes para iniciativa por dado:
1. Líder de cada lado rola pool tático; maior total escolhe primeiro.
2. Todos rolam individualmente; maior total age primeiro.
3. Rating fixo = soma de dois traits (ex: Physical + Mental).
4. Rating fixo + d6 (d8 se distinction relevante, d4 se hindering).

## Dramatic Order (p.98)

Para conflito character-driven. O **dramatic lead** declara, rola primeiro, oposição tenta superar. Se múltiplos jogadores querem ir primeiro: todos rolam, maior total vira dramatic lead.

## Scale (pp.99-100)

### Advantage of Scale

Lado com vantagem: bonus d8 ao pool + mantém um dado adicional no total. d8 d8 scale = vantagem esmagadora.

### Multi-Level Scale

Scale die pode ser d4-d12. Pode ser dividido em dados menores (d12 = d10+d10 ou d8+d8+d8 ou d6+d6+d6+d6). Independente de quantos dados adicionados, só mantém **um** dado adicional no total.

## Ganging Up (p.100)

Cada oponente adicional: +1 dado ao pool da oposição = maior trait aplicável. Não muda quantidade de dados mantidos para total.

Quando jogador supera dificuldade contra grupo: compara effect die com supporting dice. Elimina um supporting die menor que effect die. Heroic success: step up effect die (um target) ou dois effect dice (dois targets).

### PCs Ganging Up (p.100)

PC contribui dado de tipo apropriado ao PC líder. Risco: se oponente vence, effect die pode eliminar o dado contribuído, e o PC ajudante é taken out. PP = complication em vez de taken out, mas não pode mais ajudar.

Alternativa mais segura: PC usa turno para criar asset e passar ao outro PC.

## Timed Tests (pp.101-103)

Countdown em beats. GM define número de tests necessários, difficulty dice, e beat budget.

**Por rolagem:**
- Supera: custa 1 beat
- Heroic success: custa 0 beats (grátis)
- Falha: avança mas custa 2 beats

**Resultado:** beats restantes = sucesso total. Zero beats = sucesso condicional (escolher entre objetivo completo e benefício secundário). Beats esgotados antes de completar = falha.

**Buying Time:** outro PC faz test separado. Sucesso = +1 beat. Heroic success = +2 beats. Falha = não pode mais ajudar. Uma tentativa entre cada beat.

## Giving In (pp.21, 33)

Durante contest, após rolar pelo menos uma vez: definir falha nos próprios termos, ganhar PP, não pode reiniciar contra mesmo oponente. Sem PP se der in antes de rolar.

---

# Parte 8: SFX e Limits (pp.61-63)

## Construção de SFX (p.62)

SFX = combinação de cost + benefit.

**Costs:** gastar PP; step down dado benéfico; step up dado não-benéfico; escolher algo arriscado; criar d8 complication; shut down trait set.

**Benefits:** ganhar PP; adicionar d6 ao pool; step up dado benéfico; doubling; step down complication; detalhe narrativo; renomear complication; reroll de um dado; criar d8 asset.

### Dice Tricks (p.62)

- **Step up:** aumentar tamanho em um
- **Step down:** diminuir tamanho em um
- **Reroll:** rolar de novo, ignorar resultado anterior
- **Doubling:** adicionar outro dado do mesmo tamanho ao pool

### Seis SFX Standard (p.63)

| SFX | Efeito |
|---|---|
| **Exchange** | Step up ou double um dado útil para a cena; step down outro até recovery |
| **Price** | Step up/double dado útil OU d8 asset; mas também d8 complication |
| **Swap** | Gastar PP para usar dado diferente do normal, baseado na distinction |
| **Edit** | Gastar PP para declarar algo benéfico verdadeiro na ficção |
| **Folly** | Ganhar PP ao escolher algo detrimental pela distinction |
| **Shutdown** | Ganhar PP ao perder acesso a attributes/skills/roles pela cena |

## Limits (p.63)

Vulnerabilidades que concedem PP. Formato: shutdown + PP. Recovery condition específica. GM pode ativar gastando PP (mas não ganha PP para o jogador); GM oferece primeiro ao jogador.

---

# Parte 9: Criação de Personagem (pp.68-80)

## Archetypes (pp.68-69)

Personagem pré-construído parcial. Steps: selecionar archetype, escolher 2 distinction SFX para destravar, selecionar 1 de 2 signature assets listados. Highlight skills de distinctions do archetype começam d6+. 9 pontos para step up skills. GM pode capar em d10. 3 specialties + 1 extra se Know ≥ d6.

## Scratch-Built (pp.70-71)

1. **Ajustar Attributes:** Physical, Mental, Social começam d8. Pode step down um para step up outro. Nada abaixo d6 ou acima d10.
2. **Escolher 3 Distinctions** com highlight skills.
3. **Escolher Distinction SFX:** 3 Hinder (grátis) + 2 adicionais.
4. **Step Up Skills:** highlight skills primeiro, depois 9 pontos (cada ponto = 1 step).
5. **Specialties e Signature Assets:** 5 pontos. Cada: 1 specialty d6+, 1 sig asset d6, ou step up d6 sig asset para d8.
6. **Biographical info.**

### Variantes por Trait Set

- **Affiliations:** d8 em todas; adicionais começam d6
- **Roles:** pular stage 4; arrays fixos por contagem
- **Values:** d8 primeiros três, d6 resto; step up = step down outro
- **Powers:** 2 power sets em stage 3 (se supers comuns), cada com 2 SFX e 1 limit
- **Relationships:** d6 com cada PC grátis; step up via stage 5
- **Resources:** 1 ponto stage 5 = d6d6 com 2 tags

## Pathways (pp.73-80)

Criação colaborativa em 9 stages (Major/Standard/Meta). Cada stage: conectar personagem a elemento, ganhar trait. Navigation constraint: cada escolha deve ser diretamente abaixo ou ±1 coluna da anterior.

**Standard stage:** +1 resource/sig asset/skill/specialty (d6 ou step up existente).
**Major stage:** +2 elementos + same as standard + distinction.
**Meta stage:** +1 elemento + opção especial + same as major + power set/ability opcional.

---

# Parte 10: Crescimento de Personagem (pp.82-85)

## Session Records (p.82)

**Callbacks:** referenciar evento de sessão passada para benefício = PP (ativar SFX, manter dado extra, criar asset). Cada sessão específica: callback uma vez por sessão.

**Training Up:** gastar sessões para melhorias permanentes:

| Custo | Melhoria |
|---|---|
| 1 sessão | Session asset → signature asset (ou relationship) |
| 1 sessão | Trocar distinction (ou trait statement) |
| 2 sessões | Step up signature asset (ou relationship) |
| 2 sessões | Nova specialty |
| 2 sessões | Destravar novo SFX |
| 3 sessões | Step up skill (ou resource, role, value, power) |
| 4 sessões | Step up attribute (ou affiliation) + step down outro |

## Growth Pool (p.83)

Advancement via pool de dados construído ao longo do jogo (challenging statements, recovery com ajuda).

**Tag Scenes:** fim de sessão. Reescrever statements (restaura rating) ou manter (rating reduzido). Rolar growth pool + maior stress/complication da sessão vs dificuldade (trait target level + die por tipo de trait).

## Milestones (pp.84-85)

Dois milestones por personagem: um do grupo, um pessoal. Três tiers de XP:

- **1 XP:** repetível (ou 1x por test/contest)
- **3 XP:** 1x por cena
- **10 XP:** 1x por sessão (shared: indisponível até próxima sessão; personal: fecha o milestone)

## XP Unlockables (p.85)

| XP | Opção |
|---|---|
| 5 | Specialty Expert d8; destravar SFX; d6 signature asset |
| 10 | d8 signature asset; novo SFX trancado; upgrade d6→d8; specialty Expert→Master d10 |
| 15 | upgrade d8→d10; specialty Master→Grandmaster d12; d10 signature asset |
| 20 | upgrade d10→d12; d12 signature asset |

---

# Parte 11: Power List (pp.186-197)

## Descrições de Powers

Cada power tem die rating d6-d12 escalando com escopo/potência. Algumas começam em d8 porque d6 = nível humano (Durability, Intelligence, Reflexes, Stamina, Strength).

### Attack Powers (p.186)

d6: armas de fogo leves, armas corpo-a-corpo perigosas. d8: rifles automáticos, granadas. d10: explosivos pesados, relâmpagos. d12: devastação concentrada.

### Durability (p.187)

d8: pele endurecida, resistência a trauma contuso. d10: à prova de balas, temperaturas extremas. d12: invulnerabilidade convencional.

### Elemental Control (pp.187-188)

Especificar elemento (Air, Cosmic, Earth, Electric, Fire/Heat, Gravity, Ice/Cold, Kinetic/Telekinetic, Light, Magnetic, Negative, Sonic, Weather, Water).

d6 Influence: controle menor. d8 Control: local significativo. d10 Mastery: escala urbana. d12 Supremacy: escala regional.

### Intangibility (p.188)

d6: dispersão molecular leve. d8: fluir por buracos mínimos. d10: ghostlike, fora de fase. d12: completamente fora de fase incluindo energia.

### Intelligence (pp.188-189)

d8: problemas mentais complexos, cálculo, recall. d10: computador vivo, operações simultâneas. d12: além de computadores terrestres.

### Invisibility (pp.189-190)

d6: blur visual. d8: camaleão/transparência ghostlike. d10: completamente invisível visualmente. d12: indetectável por qualquer meio visual.

### Mimic (p.189)

Manifestar poder: criar asset com test/contest usando Mimic die. Rating do Mimic limita escopo do poder copiado.

### Movement Powers (pp.189-190)

**Speed:** d6 humano mais rápido, d8 cavalo, d10 trem-bala, d12 ao redor do mundo.
**Flight:** d6 helicóptero, d8 avião, d10 caça, d12 interplanetário.

Movement d8+: inclui sobrevivência ambiental.

### Psychic Powers (pp.190-191)

**Mind Control:** d6 empurrar inclinações, d8 override impulsos, d10 controle motor, d12 posse completa.
**Telepathy:** d6 link mental, d8 pensamentos superficiais, d10 sondar memórias, d12 skim pensamentos planetários.

### Reflexes (p.191)

d8: 2-3x humano. d10: ~10x humano. d12: reage como se mundo desacelerasse.

### Resistance (p.191)

Tipos: Mystic, Psychic. d6: leve. d8: enhanced. d10: superhuman. d12: nigh-invulnerable.

### Senses (pp.191-192)

d6: sentidos adicionais. d8: predatório. d10: além da natureza. d12: percepção cósmica.

### Shapeshift (p.192)

d6: mudanças menores. d8: forma externa de outro. d10: shift celular completo. d12: qualquer coisa, vivo ou não.

### Size-Changing (p.192)

**Grow:** d6 bulk up, d8 ~15ft, d10 building-sized, d12 massivo sem limite.
**Shrink:** d6 comprimir massa, d8 boneca, d10 inseto, d12 submolecular.

Não pode usar Grow e Shrink simultaneamente.

### Sorcery (p.192)

d6: truques. d8: invocação real. d10: grandes poderes místicos. d12: poder que abala o mundo. Geralmente não inflige stress diretamente, mas cria assets/complications.

### Stamina (pp.192-193)

d8: recuperação rápida, resistir doenças menores. d10: recovery rápida de ferimento, resistir maioria das doenças. d12: recovery extremamente rápida, esforço quase ilimitado.

### Strength (p.193)

d8: virar carros, dobrar barras de ferro. d10: arremessar veículos, esmagar metal. d12: arremessar objetos à órbita.

### Stretch (p.194)

d6: alcance de uma sala. d8: rua/edifício. d10: vários quarteirões. d12: distâncias absurdas.

### Teleport (p.194)

d6: blink em sala. d8: vários km (metrópole). d10: ao redor do mundo. d12: outros planetas/galáxias.

### Transmutation (p.194)

d6: afetar integridade. d8: alterar propriedades. d10: nível químico/elemental. d12: mudar qualquer objeto.

## Power SFX (pp.195-197)

| SFX | Efeito Mecânico |
|---|---|
| **Absorption** | Sucesso em contest de [tipo]: converter effect die da oposição em stunt asset OU step up power para próximo roll |
| **Afflict** | Adicionar d6 e step up effect die ao infligir [tipo] complication |
| **Area Attack** | PP para adicionar d6 e manter effect die extra por target adicional |
| **Boost** | Shut down maior power do set para step up outro power |
| **Burst** | Step up/double power die contra single target; remover maior dado do pool, somar 3 dados para total |
| **Constructs** | Adicionar d6 e step up effect die ao criar assets com [power set] |
| **Dangerous** | Adicionar d6 para ataque, step down maior dado do pool; step up effect die |
| **Focus** | Substituir dois dados iguais por um dado um step maior |
| **Healing** | Adicionar [power] ao pool para recovery de outros; PP para recover complication própria/alheia |
| **Immunity** | PP para ignorar complications de [tipo de ataque] |
| **Invulnerable** | PP para ignorar [tipo de complication] exceto por [tipo específico] |
| **Multipower** | Usar 2+ powers do set; cada power faz step down por power adicional |
| **Second Chance** | PP para reroll usando qualquer power do set |
| **Second Wind** | Dar complication ao GM; step up power para esta rolagem |
| **Unleashed** | Step up/double power para uma rolagem; falha = complication do tamanho do power die |
| **Versatile** | Dividir power die em 2 dados step down 1, ou 3 dados step down 2 |

## Power Limits (pp.197-198)

| Limit | Efeito | Restore |
|---|---|---|
| **Conscious Activation** | Shut down set se taken out/dormindo | Ao acordar |
| **Exhausted** | Shut down power específico, ganhar PP | Opportunity |
| **Gear** | Shut down set, ganhar PP | Test para restore |
| **Growing Dread** | 1 e 2 contam como hitches | Permanente |
| **Mutually Exclusive** | Shut down set A para ativar set B | Shut down B |
| **Uncontrollable** | Power vira complication, ganhar PP | Opportunity ou remover complication |

---

# Parte 12: Ability List (pp.198-216)

Powers e Abilities são **mutuamente exclusivos**. Cada ability tem die rating, effect category (Attack/Sensory/Movement/Control/Defense/Enhancement), descriptors, limits, e SFX (1 grátis na criação; destravam em d8 e d12).

**Regra de step down de effect die (p.198):** comparar effect die com ability die do atacante. Se effect die ≥ ability die: step down effect die da oposição. Se effect die > ability die: ignorar effect die da oposição completamente.

As 42 abilities são listadas abaixo com seus efeitos mecânicos primários:

| Ability | Categories | Efeitos Mecânicos Chave |
|---|---|---|
| Absorption | Defense, Enhancement | Step down effect die de energy attacks; absorver para criar asset |
| Adaptation | Defense, Enhancement | Adaptar fisiologia a condições; estender a outros |
| Animal Control | Control, Sensory | Ver pelos olhos do animal; invocar animal controlável |
| Animal Mimicry | Enhancement | Mimetizar habilidades naturais; combinar de dois animais |
| Astral Projection | Sensory, Movement | Espionar invisível; levar outros; projetar corpo parcial |
| Blast | Attack | Área de efeito; destruir objetos; aprisionar em gelo |
| Body Transformation | Defense, Enhancement | Formas alternativas (metal/líquido/gasoso); ignorar stress físico |
| Chi Mastery | Attack, Defense, Enhancement | Step up effect die para ataque; recuperar stress próprio |
| Claws | Attack | Step up effect die ao causar stress/complications |
| Combustion | Attack, Control | Explosões; bombas-relógio; escape via distração |
| Comprehension | Sensory, Enhancement | Entender idiomas instantaneamente; decifrar tecnologia alien |
| Cryokinesis | Attack, Control | Aprisionar em gelo; paredes de gelo; congelar líquidos |
| Density Control | Defense, Movement, Attack | Atravessar paredes; endurecer; punhos super-densos |
| Dream Manipulation | Sensory, Control | Entrar sonhos; criar itens em sonhos; forçar memórias |
| Duplication | Enhancement | Criar duplicatas com abilities stepped down; compartilhar stress |
| Earth Control | Attack, Control, Defense | Terremotos; barreiras de pedra; engolir veículos |
| Electrokinesis | Attack, Control | Tempestades; EMP para desabilitar eletrônicos |
| Energy Aura | Defense, Attack | Proteger outros; step down effect die de ataque; step up melee |
| Flight | Movement | Carregar objetos; dive bomb (step up effect die) |
| Force Constructs | Control, Defense | Paredes de força; redes; path through air |
| Force Field | Defense | Step down stress/complications dentro do campo |
| Gravity Control | Control, Movement | Prender com gravidade; voar; arremessar fora da cena |
| Healing | Enhancement | Recuperar stress/complications de outros; transferir para si |
| Hydrokinesis | Attack, Control, Defense | Maremotos; bolhas de ar; paredes de água |
| Illusions | Sensory, Control | Ilusões multisensoriais; step up/down effect die emocional |
| Insect Control | Control, Sensory | Enxames como d8 stunt; ver por olhos de inseto |
| Invisibility | Movement, Sensory | Escape de cena; vigiar sem ser notado; tornar outros invisíveis |
| Invulnerability | Defense | Step down effect die; recuperar stress; ignorar condições extremas |
| Light Control | Attack, Sensory | Cegar todos na cena; hipnotizar; queimar objetos |
| Luck | Enhancement | Reroll de hitch; forçar oponente rerollar maior dado |
| Magnetism | Attack, Control | Prender em metal; scramble eletrônicos; manipular ferro no sangue |
| Metahuman Sense | Sensory | Sentir abilities de outros; identificar limits; rastrear metahumanos |
| Mind Control | Control | Sugestão pós-hipnótica; apagar memórias; implantar memórias falsas |
| Paralysis | Control, Attack | Imobilizar; agente paralisante como d8 stunt |
| Plant Control | Control, Attack | Vinhas como d8 stunt; toxinas vegetais |
| Poison | Attack | Área de efeito gasoso; veneno de ativação atrasada |
| Possession | Control | Posse de GMC minor; usar SFX alheio |
| Power Leech | Control, Enhancement | Roubar ability; shut down ability alheia |
| Precognition | Sensory, Enhancement | Remover maior dado da próxima rolagem do oponente; reroll |
| Pyrokinesis | Attack, Control | Derreter objetos; aprisionar em fogo; absorver calor |
| Regeneration | Defense, Enhancement | Recuperar stress; curar qualquer doença; retornar da morte (step down ability) |
| Shadow Control | Attack, Control | Restringir com sombra; escuridão na cena inteira |
| Shadow Walk | Movement | Entrar sombra e sair de outra; portais de sombra |
| Shapeshifting | Enhancement, Defense | Mudar para objeto/animal; crescer/encolher; imitar fingerprints |
| Size Alteration | Enhancement, Attack, Defense | Crescer para intimidar; encolher para escape; interferir em contest |
| Sonic Blast | Attack | Afetar todos que ouvem; terremoto localizado; quebrar vidro |
| Stretching | Movement, Defense | Passar por espaços estreitos; step down effect die físico |
| Summoning | Control, Enhancement | Invocar criatura como d8 d8 extra |
| Super-Senses | Sensory | Ver através de objetos; ouvir/ver em outra cena; rastrear por cheiro |
| Super-Speed | Movement | Entrar qualquer cena; múltiplas atividades; correr sobre água |
| Super-Strength | Attack, Enhancement | Feitos fantásticos; arremessar fora da cena; shockwave |
| Swimming | Movement | Alta velocidade aquática; escape pela água |
| Technopathy | Control, Sensory | Controlar eletrônicos; override segurança; ver por câmeras |
| Telekinesis | Attack, Defense, Movement | Arremessar fora de cena; escudo TK; mover objetos pesados |
| Telepathy | Sensory, Control | Ler pensamentos; mensagens psíquicas; escudo mental |
| Teleportation | Movement | Entrar qualquer cena; portais; levar outros |
| Time Control | Control, Enhancement | Parar tempo; reverter para reroll; slow time |
| Time Travel | Movement, Enhancement | Escape temporal; mensagem do futuro; levar outros |
| Transmute | Control, Enhancement | Criar ferramentas (d8 stunt); buracos em paredes; bombas |
| Tunneling | Movement, Attack | Túneis como d8 stunts; escape; step up effect die com garras |
| Wall Walking | Movement | Emboscada do teto; escape por parede; levar outros |
| Wind Control | Attack, Control, Movement | Tornado localizado; prender com rajadas; voar curta distância |

---

# Parte 13: Gear como Abilities (p.217)

Qualquer ability pode ser replicada como device. Gear funciona como abilities com **Gear limit universal**: pode ser perdido, quebrado ou roubado (shut down, ganhar PP; test para restore).

**Ablative Armor mod:** armor ability die vs attacker ability die. Se armor > attacker: effect die ignorado, armor step down. Se armor ≤ attacker: effect die step down, armor step down.

**Weapon Ranges mod:** difficulty die adicionado à oposição baseado em range. "A stretch" = d8. "Almost impossible" = d12.

---

# Parte 14: Fantasy Milestones (pp.218-219)

12 milestone templates com triggers em 1/3/10 XP. O trigger de 10 XP sempre apresenta escolha binária narrativa.

| Milestone | 1 XP | 3 XP | 10 XP |
|---|---|---|---|
| Accursed | Ataque demonstra natureza sinistra | Adicionar ≥d8 ao doom pool | Reivindicado por poder vilão OU golpe major contra poder vilão |
| Ascetic | Abster-se de prazer mundano | Participar de indulgência problemática | Fundar instituição de abstinência OU abandonar caminho ascético |
| Blessed | Realizar rito religioso | Infligir stress em blasfemador | Completar grande obra divina OU tornar-se mártir |
| Comfortable in Shadows | Esconder-se/ficar fora do spotlight | Sair das sombras para algo importante | Entrar no spotlight publicamente OU desaparecer para sempre |
| Haughty Noble | Comentário desdenhoso sobre classe baixa | Tentar comprar saída de problema | Abandonar nobreza OU abraçar vida nobre |
| Homebody | Algo lembra de casa | Fazer algo aventureiro impossível em casa | Aposentar em casa OU abraçar vida aventureira |
| Honorable Warrior | Declarar honra/desonra | Aceitar risco de stress pela honra | Ato desonroso pelo bem maior OU sacrifício pela honra |
| Leader | Dar ordem ao grupo | Membro usa asset que você criou | Reconhecido por conquistas OU deposto em motim |
| Mysterious Sage | Observação críptica | Encontrar algo inexplicável | Exposto como não tão sábio OU alguém é o Chosen One |
| Nature's Guardian | Eschew artificial por natural | Criar asset para outro | Dar a vida pela natureza OU permitir dano à natureza |
| Planar Traveler | Seguir costume estranho aos companheiros | Desligar do mundo material | Preso ao mundo material OU partir para outro |
| Treasure Hunter | Adquirir ou gastar dinheiro | Buscar tesouro durante batalha | Encontrar o grande score OU gastar tudo em altruísmo |

---

# Parte 15: Motor Pool / Veículos (pp.220-222)

## Traits de Veículos

**Atributos:** Engines (agilidade/velocidade), Frame (integridade), Systems (suporte de vida/comms/computadores), Crew (habilidade da tripulação GMC; veículos operados por PC não têm).

**Distinctions:** três categorias (Model, History, Customization). Cada uma com Hinder SFX grátis. Model determina atributos base, não pode ser trocado.

**Signature Assets:** modificações/recursos, tipicamente d8.

## Usando Veículos

Pool: pair 1 PC prime trait com vehicle trait. Atributo do veículo **substitui** (não adiciona a) atributo do PC. Distinctions e sig assets complementam.

Sucesso/falha do veículo afeta o grupo inteiro. Hitches geram complications do veículo. PP pode evitar takeout do veículo.

## Construindo Veículo (p.222)

1. **Model:** d8/d8/d8 em Engines/Frame/Systems. Step up até +2, step down outro pelo mesmo total. Opções: d12/d8/d4, d12/d6/d6, d10/d8/d6, d8/d8/d8.
2. **2 Distinctions adicionais** (History + Customization).
3. **Distinction SFX:** Hinder grátis + 2 adicionais.
4. **2 Signature Assets** a d8.
5. **Nomear.**

Avanço: gastar sessão para melhorar veículo (trocar distinctions exceto model, add/step up sig assets, destravar SFX). PCs podem poolar sessões.

---

# Parte 16: Glossário Mecânico

## Resolução Core

| Termo | Definição |
|---|---|
| **Action** (p.24, 98) | Mod que substitui tests/contests por ação/reação com turnos |
| **Beat** (p.88) | Unidade subjetiva de tempo para um test |
| **Test** (p.18) | Uso dos dados para determinar resultado, precisa superar dificuldade |
| **Contest** (p.19) | Série de rolagens entre oponentes até give in ou falha |
| **Reaction** (p.24, 98) | Rolagem de oposição para superar ação |

## Dados e Resultados

| Termo | Definição |
|---|---|
| **Dice Pool** (p.17) | Todos os dados rolados num test/contest |
| **Total** (p.16) | Soma de pelo menos dois dados após rolar |
| **Difficulty** (p.18) | Medida de quão difícil é ter sucesso |
| **Hitch** (p.17) | Dado que rolou 1; GM pode dar PP e criar complication |
| **Opportunity** (p.37) | Hitch do GM; jogador gasta PP para step down complication ou step up asset |
| **Botch** (p.17) | Todos os dados são hitches; total = 0; complication grátis |
| **Effect Die** (p.20) | Dado restante usado para criar assets/complications; só tamanho importa |
| **Heroic Success** (p.20) | Total 5+ acima da dificuldade |

## Modificações de Dados

| Termo | Definição |
|---|---|
| **Step Up** (p.16) | Trocar dado pelo próximo maior |
| **Step Down** (p.16) | Trocar dado pelo próximo menor |
| **Reroll** (p.62) | Rolar dado novamente |
| **Doubling** (p.62) | Adicionar dado do mesmo tamanho ao pool |

## Tipos de Personagem

| Termo | Definição |
|---|---|
| **PC** | Personagem jogador |
| **GMC Major** (p.114) | Stats ~equivalentes a PC, nome e papel significativo |
| **GMC Minor** (p.115) | Poucos stats, pode ou não ter nome |
| **Extra** (p.116) | Single trait, sem nome individual |
| **Mob** (p.117) | Grupo de extras como personagem único com múltiplos dados |
| **Boss** (p.118) | GMC único com múltiplos dados como mob trait |
| **Faction** (p.116) | Grupo com ideologia; funciona como mob com scale die |

## Tipos de Cena

| Tipo | Mecânica |
|---|---|
| **Opening** (p.89) | Framing puro, sem tests |
| **Action** (p.89) | Conflito ativo |
| **Bridge** (p.89) | Downtime e recovery |
| **Exploration** (p.89) | Investigação e descoberta |
| **Flashback** (p.89) | Cena no passado para criar assets |
| **Tag** (p.89) | Fim de sessão, growth |

---

# Resumo: Estado que o Bot Precisa Rastrear

## Por Personagem

1. **Trait sets** (configurável por jogo): nome, die rating, SFX (travado/destravado), statements
2. **Distinctions** (3): nome, d8, Hinder + SFX adicionais
3. **Die ratings** como valores discretos: {d4, d6, d8, d10, d12}
4. **SFX** por trait: trigger, cost, benefit, estado
5. **Limits** por power set: trigger, shutdown, recovery
6. **Plot Points** (inteiro)
7. **Signature assets**: nome, die rating, SFX
8. **Specialties**: nome, skill-pai, die rating
9. **Resources**: nome, dice pool, tags, gastos/disponíveis
10. **Stress dice** (um por tipo, d4-d12; além d12 = stressed out)
11. **Trauma dice** (um por tipo, d4-d12; além d12 = permanente)
12. **Complications** (nomeadas, die rating; além d12 = taken out)
13. **Assets temporários** (nomeados, die rating)
14. **Hero dice** banked
15. **Growth tracking**: session records, growth pool, XP, milestones (1/3/10 XP tiers)
16. **Values**: ratings com constraint fixed-total

## Por Cena

1. **Tipo de cena** (determina subsistemas ativos)
2. **Action order state** (quem agiu, action lead atual)
3. **Timed test state** (beats restantes, tests completados, dificuldade por stage)
4. **Doom pool** (dados do GM)
5. **Crisis pools** (dados por problema localizado)
6. **Taken-out status** por personagem
7. **Scene complications/assets** (ativos na cena)
