"""Accessible text formatter for all bot output.

All output is linear text, no box art, no emoji-only information.
Screen reader friendly.
"""

from cortex_bot.models.dice import die_label


HITCH_DIE_SCALE = {1: 6, 2: 8, 3: 10}


def _hitch_die_size(hitch_count: int) -> int:
    """Return complication die size for given hitch count (1→d6, 2→d8, 3→d10, 4+→d12)."""
    return HITCH_DIE_SCALE.get(hitch_count, 12)


def _format_dice_detail(results: list[tuple[int, int]], hitches: list[tuple[int, int]] | None) -> str:
    """Format individual dice results as parenthetical detail."""
    parts = []
    for size, value in results:
        part = f"{die_label(size)} rolled {value}"
        if hitches and (size, value) in hitches:
            part += " (hitch)"
        parts.append(part)
    return ", ".join(parts)


def format_roll_result(
    player_name: str,
    results: list[tuple[int, int]],
    included_assets: list[str] | None = None,
    hitches: list[tuple[int, int]] | None = None,
    is_botch: bool = False,
    best_options: list[dict] | None = None,
    difficulty: int | None = None,
    available_assets: list[dict] | None = None,
    opposition_elements: list[str] | None = None,
    doom_enabled: bool = False,
) -> str:
    lines: list[str] = []

    lines.append(f"{player_name} rolled {len(results)} dice.")

    if included_assets:
        lines.append(f"Included: {', '.join(included_assets)}.")

    if is_botch:
        detail = _format_dice_detail(results, hitches)
        lines.append(
            f"Botch. Total zero ({detail}). "
            "GM creates a free d6 complication, step up for each additional hitch."
        )
        return "\n".join(lines)

    if hitches:
        hitch_dice = [die_label(s) for s, _ in hitches]
        comp_die = die_label(_hitch_die_size(len(hitches)))
        if doom_enabled:
            lines.append(
                f"Hitches: {', '.join(hitch_dice)}. "
                f"GM may award 1 PP and create a {comp_die} complication, "
                "or add a die to the Doom Pool."
            )
        else:
            lines.append(
                f"Hitches: {', '.join(hitch_dice)}. "
                f"GM may award 1 PP and create a {comp_die} complication."
            )

    detail = _format_dice_detail(results, hitches)

    if best_options:
        lines.append(detail + ".")
        for opt in best_options:
            opt_detail = (
                f"{die_label(opt['dice'][0][0])} rolled {opt['dice'][0][1]}, "
                f"{die_label(opt['dice'][1][0])} rolled {opt['dice'][1][1]}"
            )
            status = ""
            if difficulty is not None:
                margin = opt["total"] - difficulty
                if margin > 0:
                    if margin >= 5:
                        step_ups = margin // 5
                        status = (
                            f" Heroic success, margin {margin}. "
                            f"Effect die steps up {step_ups} time(s)."
                        )
                    else:
                        status = f" Success, margin {margin}."
                else:
                    status = f" Failure, short by {abs(margin)}."
            lines.append(
                f"{opt['label']}: {opt['total']} ({opt_detail}). "
                f"Effect die: {die_label(opt['effect_size'])}.{status}"
            )
    else:
        non_hitch = [(s, v) for s, v in results if v != 1]
        if len(non_hitch) >= 2:
            non_hitch.sort(key=lambda x: x[1], reverse=True)
            total = non_hitch[0][1] + non_hitch[1][1]
            effect = non_hitch[2] if len(non_hitch) > 2 else None
            status = ""
            if difficulty is not None:
                margin = total - difficulty
                if margin > 0:
                    if margin >= 5:
                        step_ups = margin // 5
                        status = (
                            f" Heroic success, margin {margin}. "
                            f"Effect die steps up {step_ups} time(s)."
                        )
                    else:
                        status = f" Success, margin {margin}."
                else:
                    status = f" Failure, short by {abs(margin)}."
            total_str = f"Total {total} ({detail}).{status}"
            if effect:
                total_str += f" Effect die: {die_label(effect[0])}."
            lines.append(total_str)
        elif len(non_hitch) == 1:
            lines.append(
                f"Total {non_hitch[0][1]} ({detail}). "
                "No effect die available, default d4."
            )

    if available_assets:
        asset_strs = [f"{a['name']} {die_label(a['die_size'])}" for a in available_assets]
        lines.append(f"Available assets: {', '.join(asset_strs)}.")

    if opposition_elements:
        lines.append(
            f"Opposition pool: {', '.join(opposition_elements)}."
        )

    return "\n".join(lines)


def format_campaign_info(
    campaign: dict,
    players: list[dict],
    player_states: dict,
    scene: dict | None,
    doom_pool: list[dict] | None,
    scene_assets: list[dict] | None = None,
    scene_complications: list[dict] | None = None,
    crisis_pools: list[dict] | None = None,
    config: dict | None = None,
) -> str:
    lines: list[str] = []

    scene_name = scene["name"] if scene else "none"
    lines.append(f"CAMPAIGN: {campaign['name']}")
    lines.append(f"Active scene: {scene_name}")
    lines.append("")

    for i, p in enumerate(players):
        if i > 0:
            lines.append("")
        pid = p["id"]
        state = player_states.get(pid, {})

        name_line = p["name"].upper()
        if p["is_gm"]:
            name_line += " (GM)"
        elif p.get("is_delegate"):
            name_line += " (delegate)"
        lines.append(name_line)

        stress_list = state.get("stress", [])
        if stress_list:
            stress_strs = [
                f"{s['stress_type_name']} {die_label(s['die_size'])}"
                for s in stress_list
            ]
            lines.append(f"Stress: {', '.join(stress_strs)}")
        else:
            lines.append("Stress: none")

        trauma_list = state.get("trauma", [])
        if trauma_list:
            trauma_strs = [
                f"{t['stress_type_name']} {die_label(t['die_size'])}"
                for t in trauma_list
            ]
            lines.append(f"Trauma: {', '.join(trauma_strs)}")

        assets_list = state.get("assets", [])
        if assets_list:
            asset_strs = [
                f"{a['name']} {die_label(a['die_size'])} ({a['duration']})"
                for a in assets_list
            ]
            lines.append(f"Assets: {', '.join(asset_strs)}")
        else:
            lines.append("Assets: none")

        complications_list = state.get("complications", [])
        if complications_list:
            comp_strs = [
                f"{c['name']} {die_label(c['die_size'])}"
                for c in complications_list
            ]
            lines.append(f"Complications: {', '.join(comp_strs)}")
        else:
            lines.append("Complications: none")

        hero_list = state.get("hero_dice", [])
        if hero_list:
            hero_strs = [die_label(h["die_size"]) for h in hero_list]
            lines.append(f"Hero dice: {', '.join(hero_strs)}")

        lines.append(f"PP {p['pp']}, XP {p['xp']}")

    has_scene_elements = scene_assets or scene_complications or crisis_pools
    if has_scene_elements:
        lines.append("")
        lines.append("SCENE ELEMENTS")
        if scene_assets:
            asset_strs = [
                f"{a['name']} {die_label(a['die_size'])}"
                for a in scene_assets
            ]
            lines.append(f"Scene assets: {', '.join(asset_strs)}")
        if scene_complications:
            comp_strs = [
                f"{c['name']} {die_label(c['die_size'])}"
                for c in scene_complications
            ]
            lines.append(f"Scene complications: {', '.join(comp_strs)}")
        if crisis_pools:
            for cp in crisis_pools:
                dice_strs = [die_label(d["die_size"]) for d in cp.get("dice", [])]
                lines.append(f"Crisis Pool '{cp['name']}': {', '.join(dice_strs)}")

    if doom_pool is not None:
        lines.append("")
        lines.append("DOOM POOL")
        if doom_pool:
            doom_strs = [die_label(d["die_size"]) for d in doom_pool]
            lines.append(", ".join(doom_strs))
        else:
            lines.append("empty")

    if config is not None:
        lines.append("")
        lines.append("MODULES")
        for module in ("doom_pool", "hero_dice", "trauma", "best_mode"):
            status = "active" if config.get(module) else "inactive"
            lines.append(f"{module}: {status}")

    return "\n".join(lines)


def format_scene_end(
    scene_name: str | None,
    removed_assets: list[dict],
    removed_complications: list[dict],
    removed_crisis_pools: list[dict],
    stress_changes: list[dict] | None = None,
    persistent_state: str = "",
) -> str:
    lines: list[str] = []
    label = scene_name or "unnamed"
    lines.append(f"SCENE ENDED: {label}")

    has_removals = removed_assets or removed_complications or removed_crisis_pools
    if has_removals:
        lines.append("")
        lines.append("REMOVED (scene scope)")
        if removed_assets:
            for a in removed_assets:
                owner = a.get("player_name", "scene")
                lines.append(f"  {a['name']} {die_label(a['die_size'])} ({owner})")
        if removed_complications:
            for c in removed_complications:
                owner = c.get("player_name", "scene")
                lines.append(f"  {c['name']} {die_label(c['die_size'])} ({owner})")
        if removed_crisis_pools:
            for cp in removed_crisis_pools:
                lines.append(f"  {cp['name']}")

    if stress_changes:
        lines.append("")
        lines.append("STRESS CHANGES (bridge)")
        for sc in stress_changes:
            if sc.get("eliminated"):
                lines.append(f"  {sc['player']}: {sc['type']} eliminated (was d4)")
            else:
                lines.append(
                    f"  {sc['player']}: {sc['type']} "
                    f"{die_label(sc['from'])} to {die_label(sc['to'])}"
                )

    if not has_removals and not stress_changes:
        lines.append("No scene elements to remove.")

    if persistent_state:
        lines.append(f"\n{persistent_state}")

    lines.append("")
    lines.append("Next: /scene start to begin a new scene, /campaign info to see persistent state.")

    return "\n".join(lines)


def format_action_confirm(action: str, details: str, player_state: str = "") -> str:
    msg = f"{action}. {details}"
    if player_state:
        msg += f" {player_state}"
    return msg
