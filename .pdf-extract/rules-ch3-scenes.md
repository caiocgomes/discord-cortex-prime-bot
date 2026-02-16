# Chapter 3: Prime Scenes - Mechanical Rules Reference

This document extracts all mechanically relevant rules from Chapter 3 (Prime Scenes) of the Cortex Prime Game Handbook, supplemented by the stress, trauma, and recovery rules from Chapter 1 that are directly referenced by scene mechanics. Rules are described with precision sufficient for bot implementation.

---

## Scene Structure (p.88)

A scene is the primary unit of play. The GM frames the scene (location, characters present, situation) and ends it. Scenes break down into **beats**, which are the smallest dramatic units. Each beat corresponds to one action or test a character attempts. There is no fixed number of beats per scene. A beat may represent seconds or hours of in-fiction time; what matters is that it maps to a single test or roll.

Scenes end when the primary situation is resolved, at the GM's discretion.

## Types of Scenes (p.89)

Six scene types exist, each with distinct mechanical implications:

**Opening scenes** require no tests or contests by default. They are pure framing.

**Action scenes** (p.89, p.94) are characterized by conflict and typically use tests, contests, or the action order system. These are where SFX, skills, and plot points see the most use. See "What is Conflict?" (p.97) for the mechanics that govern them.

**Bridge scenes** (p.89, p.95) represent downtime. Mechanically, these are the scenes where PCs recover from complications (p.37 rules apply), recover stress (automatic step-down by one), create or upgrade assets via tests (p.35), and eliminate complications at reduced difficulty. Bridge scenes also trigger milestone-based character growth.

**Exploration scenes** (p.89, p.95) use standard tests against the environment or abstract difficulty. They focus on acquiring clue-based assets and picking up complications.

**Flashback scenes** (p.89, p.96) allow a player to create an asset via a short scene set in the past, then return to the current scene. Prefer simple tests over contests in flashbacks. Flashbacks cannot retroactively change established events, only reveal new information or create assets.

**Tag scenes** (p.89, p.96) close a session. No contests should occur. Tests, if any, should be minimal. These are for resolving trait statements, milestone goals, and growth-related bookkeeping.

---

## Conflict and Action Order (p.97-99)

### Three Conflict Paradigms (p.97)

The game identifies three common conflict structures, each with different mechanical defaults:

**Heroes vs Villains**: Tests against minor GMCs and extras, contests against major GMCs. Use action order for set-piece scenes with multiple antagonists. Contests for one-on-one duels.

**Interpersonal Drama**: Most scenes are contests. Do not use action order unless necessary. Use dramatic order instead. Interfering rules apply liberally. Contests form the bulk of PvP drama.

**Environmental Conflict**: Players test traits against the environment or abstract difficulty. Timed tests are common. Action order only when fights with threatening elements occur.

### Dramatic Order (p.98)

When the focus is character-driven conflict over longer periods, dramatic order is the default. A character (usually a player) declares they want something, and another character opposes. The initiating character is the **dramatic lead**. Play proceeds as a standard contest: the dramatic lead rolls first, the opposition tries to beat their total, and the contest escalates or resolves per the standard contest rules.

If multiple players want to go first simultaneously, all roll their contest dice. The highest rolling player becomes the dramatic lead and uses that roll. Others pick up their dice and may interfere, assist, or sit out.

Other players in the scene can aid the dramatic lead, interfere with the contest (spending a PP to do so), or wait.

### Action Order / Handoff Initiative (p.98)

When the sequence of events matters (fights, chaos, time-pressure), use action order.

**Actions and Reactions (p.98)**: Tests and contests are replaced by actions (offensive rolls) and reactions (defensive rolls, using only defensive traits). The acting character chooses their target. If no opposing character exists, the GM uses difficulty dice as the reaction. This is the Action-Based Resolution mod (p.24): the action roll is always made first, and the reaction must exceed (not just meet) the action total to succeed.

**Who Goes First (p.98)**: The GM decides the action lead based on the fiction (who starts the fight, who has the drop, etc.).

**Turn Progression (p.98)**: All characters (PC and GMC) get one turn per round. After the action lead acts, they choose the next character (PC or GMC) to act. Once everyone has acted, the last character to go chooses the action lead for the next round (and may nominate themselves).

**Ending Action Order (p.98)**: The GM can drop out of action order at any time, such as after a decisive win or when nothing interesting can happen.

**Turn Tracking (p.98)**: Use turn markers (two-sided cards, miniature standing/lying, tokens) to track who has acted.

### Taking Initiative Mod (p.99)

This mod replaces the handoff system with a die-roll-determined order. Four variants:

1. Each side chooses a leader who assembles a pool (traits reflecting tactical/strategic ability) and rolls. Highest total side picks who goes first from their group, then next highest, and so on.
2. Everyone rolls individually; characters act from highest total to lowest.
3. Each character has a fixed initiative rating equal to the highest possible total of two traits (e.g., Physical + Mental). Act in order of that rating.
4. Each character has a fixed initiative rating from two traits but also rolls a d6 (or d8 if a relevant distinction applies, or d4 if a hindering distinction). Add the roll to the rating. Hitches on the initiative roll do not add to the total and can be activated by the GM once order is settled.

---

## Scale (p.99-100)

### Advantage of Scale (p.99)

When two sides differ radically in size or power, the side with the advantage adds a bonus d8 to their dice pool AND keeps one additional die result in their total (equivalent to a free PP spend on their total). A d8 d8 scale (keeping two additional dice) represents an overwhelming advantage and should be used sparingly.

Players can earn a scale die if they vastly outnumber or outgun opponents.

### Multi-Level Scale Mod (p.100)

The scale die can be any size from d4 to d12, each step representing a larger target. The scale die may be split into smaller dice: a d12 can become d10+d10 or d8+d8+d8 or d6+d6+d6+d6. Regardless of how many dice are added from scale, the larger-scale side only keeps one additional die in their total (not one per scale die).

When two combatants share the same scale, neither gets an advantage. The scale comparison is relative: if a medium mech (d8 scale) attacks a light mech (d6 scale), the medium mech gets the scale advantage. If the target is heavy (d10 scale), the defender gets the scale advantage on their reaction.

---

## Ganging Up (p.100)

Each additional opponent adds a single die to the opposition's pool equal to their highest applicable trait. This does not change the number of dice kept for the total (still two). Example: six Thugs d6 = roll 6d6, keep best two for total.

Every time a player beats the difficulty against a group with supporting characters, they compare their effect die to the supporting dice and knock away a single supporting die that is smaller than their effect die. This whittles down the opposition one at a time.

On a heroic success (beating difficulty by 5+), the player can either step up their effect die to take out a single supporting die, or keep two effect dice to knock out two supporting GMC dice of smaller size. Once down to a single opponent, no more dice get knocked off.

### Getting Help from Others (p.100)

A group of PCs can gang up by handing a single die of appropriate type to the leading PC. Risk: if the opponent beats the difficulty, the effect die can take out a helping PC's contributed die, and that helping PC is taken out as if they lost the fight. The helper can drop out before dice are rolled again, or spend a PP to take a complication instead of being taken out (but can no longer help the primary PC regardless).

Alternatively, a PC can use their turn to make a test and create an asset to hand to another PC (p.35), avoiding the risk of being taken out.

---

## Timed Tests (p.101-103)

A timed test handles time-pressure situations with a countdown measured in beats. Each roll by the player costs one beat. The GM sets the difficulty for each test and decides how many beats are available.

**Setup**: The GM defines the number of tests required (typically three or four), the difficulty dice for each, and the beat budget. By default, beats = number of tests. For easier tests, add one or two extra beats. For harder tests, subtract one or two beats.

**Resolution per roll**:
- Beat the difficulty: costs one beat (the roll itself).
- Heroic success (beat difficulty by 5+): costs zero beats. The roll is free.
- Fail to beat the difficulty: the task still advances to the next stage, but costs two beats (the roll plus one extra for taking too long).

**Completing the Timed Test (p.103)**: If the player finishes all required tests with beats remaining, they achieve their objective fully (clean getaway, full success). If they finish with exactly zero beats remaining, success is conditional: they must choose between full objective and some secondary benefit (clean getaway, saving resources, etc.).

**Running Out of Time (p.103)**: If beats drop to zero or below before completing all tests, the player fails and whatever consequence the GM prepared occurs. The player cannot finish their objective.

**Buying Time (p.103)**: Another PC can make a separate test to buy time. On success, the timed-test player regains one lost beat. On heroic success, two beats. On failure, that helping PC can no longer assist for the rest of the timed test. Only one buying-time attempt can happen between each beat of the timed test.

---

## Stress (p.39, Ch1 Core)

Stress is a mod that replaces the default rule of spending PP to take a complication instead of being taken out. With stress active, any time a failure at a test or contest would take a character out or cause harm, they take stress instead, without spending PP.

### Inflicting Stress (p.39)

Any attack or effect that can take a character out does the following:

- If the PC currently has no stress, or has stress at a lower die rating than the incoming effect die: the PC takes stress equal to the effect die.
- If the PC already has stress at a die rating equal to or greater than the incoming effect die: the existing stress is stepped up by one.

Example: A PC with d8 stress takes d8 additional stress, stepping up to d10. If they instead take d12 stress, the d12 replaces the d8 (since it is larger).

### Stress at d4 (p.39)

Stress rated at d4 goes into the player's own dice pool (not the opposition's) and earns the player a PP, identical to how d4 complications work. Immediately after that test or contest, the d4 stress either goes away or, if the player rolled a hitch, steps up as the condition worsens.

### Opposition Use of Stress (p.39)

Only one type of stress can be included in the opposition dice pool against a character at a time. The GM can pay the player a PP to add an additional stress die. Characters can be affected by both stress and complications simultaneously.

### Types of Stress (p.40)

Games can define one or more stress types. Common configurations:
- Physical, Mental, Social
- Afraid, Angry, Exhausted, Injured, Insecure

A game may use a single stress track or multiple typed tracks.

---

## Recovering Stress (p.40)

All stress die ratings are automatically stepped down by one during any scene specifically framed as a rest period, downtime, or transition. If back-to-back action scenes occur with no rest, no stress recovers.

To recover remaining stress beyond the automatic step-down, use the recovering complications rules (p.37): make a test vs a dice pool of d8+d8 plus the stress die. The outcomes mirror complication recovery:

- **Beat the difficulty, effect die > stress die**: stress is eliminated.
- **Beat the difficulty, effect die <= stress die**: stress steps down by one. Cannot try again until time passes.
- **Beat the difficulty but roll a hitch**: GM may spend a PP to introduce a new complication or inflict a different type of stress starting at d6.
- **Fail to beat the difficulty**: stress remains unchanged.
- **Fail and roll hitches**: stress steps up by one per hitch.

---

## Stressed Out (p.40)

If any stress die rating is ever stepped up past d12, the character is **stressed out** (taken out) and no longer participates in the scene. By default, you cannot spend a PP to delay this (unlike the base complication rule). When stressed out, the character is treated as having d12 stress for the purposes of any additional incoming stress.

---

## Pushing Stress Mod (p.40)

Players may spend a PP to add their stress die to their own dice pool (instead of it being added to the opposition pool) for that test or contest. After the roll resolves, the stress die steps up by one. This can cause the PC to be stressed out if it steps past d12.

Some SFX may grant this ability without requiring a PP; the drawback (stepping up the stress) serves as the cost.

---

## Trauma (p.41)

Trauma is long-term stress. Any time a PC's stress is stepped up past d12, they are stressed out of the scene AND gain d6 trauma of the same type as the stress that just exceeded d12. Trauma functions mechanically like stress but is much harder to recover.

### Trauma While Stressed Out (p.41)

During any scene in which a character is stressed out and has trauma, additional stress directed at the character goes directly to trauma instead.

### Permanent Removal (p.41)

If trauma is stepped up beyond d12, the character is permanently out of the game (dead, incoherent, lost, or whatever is fictionally appropriate).

### Recovering Trauma (p.41)

Recovering trauma requires a test using appropriate traits vs a base difficulty of d8+d8 plus the trauma die.

- **Beat the difficulty**: trauma steps down by one.
- **Beat the difficulty but roll a hitch**: trauma steps down, but the GM may spend a PP to introduce a complication that hinders the PC in the next scene, or inflict stress of a different type than the trauma being recovered (starting at d6, or stepping up by one if the PC already has stress of that type).
- **Fail to beat the difficulty**: trauma does not change. Cannot try again until time passes.
- **Fail and roll hitches**: trauma steps up by one per hitch. If this steps trauma past d12, the character is permanently removed.

Note: during a restful scene, stress automatically steps down by one, but trauma remains at its current level. Trauma never auto-recovers.

---

## Shaken and Stricken Mod (p.42)

This mod applies stress dice directly to specific traits (e.g., attributes or skills; the target trait set is determined before the game starts). When a character takes stress, the opponent chooses which trait receives it.

Stress applied to a trait is added to the opposition's dice pool whenever the player uses that trait. Exception: d4 stress goes into the player's own pool per standard d4 rules.

**Shaken**: If the stress applied to a trait exceeds that trait's die rating, the PC is shaken and can only keep one die for their total on any future tests/contests.

**Stricken**: If the PC is already shaken and takes stress to a second trait that would also make them shaken, they are stricken and taken out of the scene. A character also becomes stricken if any of their stress is stepped up beyond d12. Recovery follows the same rules as other stress-based mods.

---

## Giving In (p.21, p.33)

During a contest, after rolling at least once, a player may choose to give in rather than rolling to beat the opponent's total. Mechanically:

- The player defines the failure on their own terms (narrative control over how they lose).
- The player earns a PP.
- The player cannot immediately initiate another contest with the same opponent.
- The player does NOT get a PP if they give in before rolling at least once.

Giving in is distinct from losing: the loser of a contest (who fails to beat the difficulty) has their failure defined by the winner, and picks up a complication (or, in high-stakes scenes, is taken out).

---

## Being Taken Out (p.22)

Most tests and contests do not carry take-out risk. The GM must declare a scene as high-stakes for take-out to apply.

In a high-stakes contest, after winning, compare your effect die to the opposition's effect die. If yours is larger, they are taken out. If theirs is equal or larger (or they spend a PP), they take a complication equal to your effect die instead of being taken out.

When taken out, a character cannot perform tests or contests and does not participate further in the scene. The GM may rule that certain tests or SFX still function.

**Taken Out by Complications (p.22)**: If a complication on a character is stepped up beyond d12, that character is automatically taken out.

**Recovery in Scene (p.22)**: Being taken out can be reversed by other characters with healing, magic, or ability to change the circumstances. A character returning from being taken out comes back with at least a d6 complication reflecting the experience.

**Stay in the Fight (PP spend) (p.33)**: When about to be taken out, a player may spend a PP to take a complication instead. The complication size equals the opposing effect die. (Note: the stress mod replaces this rule; stress absorbs the hit without requiring a PP spend.)

---

## Summary of Bot-Critical State Tracking

For a Discord bot implementing these rules, the following state must be tracked per character per scene:

1. **Stress dice** (one per stress type, die rating from d4 to d12; past d12 = stressed out)
2. **Trauma dice** (one per stress type, die rating from d4 to d12; past d12 = permanent removal)
3. **Complications** (named, with die rating; past d12 = taken out)
4. **Assets** (named, with die rating; temporary or signature)
5. **Plot Points** (integer count)
6. **Action Order state** (who has acted this round, who is the current action lead)
7. **Timed Test state** (beats remaining, tests completed, difficulty per stage)
8. **Scene type** (determines which mechanical subsystems are active)
9. **Taken-out status** (whether a character is currently out of the scene)
