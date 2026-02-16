"""Accessible text formatter for all bot output.

All output is linear text, no box art, no emoji-only information.
Screen reader friendly.
"""

from cortex_bot.models.dice import die_label


def _format_dice_detail(results: list[tuple[int, int]], hitches: list[tuple[int, int]] | None) -> str:
    """Format individual dice results as parenthetical detail."""
    parts = []
    for size, value in results:
        part = f"{die_label(size)} tirou {value}"
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
) -> str:
    lines: list[str] = []

    lines.append(f"{player_name} rolou {len(results)} dados.")

    if included_assets:
        lines.append(f"Incluidos: {', '.join(included_assets)}.")

    if is_botch:
        detail = _format_dice_detail(results, hitches)
        lines.append(
            f"Botch. Total zero ({detail}). "
            "GM cria complication d6 gratis, step up por hitch adicional."
        )
        return "\n".join(lines)

    if hitches:
        hitch_dice = [die_label(s) for s, _ in hitches]
        lines.append(
            f"Hitches: {', '.join(hitch_dice)}. "
            "GM pode dar PP e criar complication d6, ou adicionar dado ao Doom Pool."
        )

    detail = _format_dice_detail(results, hitches)

    if best_options:
        for opt in best_options:
            opt_detail = (
                f"{die_label(opt['dice'][0][0])} tirou {opt['dice'][0][1]}, "
                f"{die_label(opt['dice'][1][0])} tirou {opt['dice'][1][1]}"
            )
            status = ""
            if difficulty is not None:
                margin = opt["total"] - difficulty
                if margin > 0:
                    if margin >= 5:
                        step_ups = margin // 5
                        status = (
                            f" Heroic success, margem {margin}. "
                            f"Effect die faz step up {step_ups} vez(es)."
                        )
                    else:
                        status = f" Sucesso, margem {margin}."
                else:
                    status = f" Falha, faltou {abs(margin)}."
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
                            f" Heroic success, margem {margin}. "
                            f"Effect die faz step up {step_ups} vez(es)."
                        )
                    else:
                        status = f" Sucesso, margem {margin}."
                else:
                    status = f" Falha, faltou {abs(margin)}."
            total_str = f"Total {total} ({detail}).{status}"
            if effect:
                total_str += f" Effect die: {die_label(effect[0])}."
            lines.append(total_str)
        elif len(non_hitch) == 1:
            lines.append(
                f"Total {non_hitch[0][1]} ({detail}). "
                "Sem effect die disponivel, default d4."
            )

    if available_assets:
        asset_strs = [f"{a['name']} {die_label(a['die_size'])}" for a in available_assets]
        lines.append(f"Assets disponiveis: {', '.join(asset_strs)}.")

    if opposition_elements:
        lines.append(
            f"Pool da oposicao: {', '.join(opposition_elements)}."
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
) -> str:
    lines: list[str] = []

    scene_name = scene["name"] if scene else "nenhuma"
    lines.append(f"Campanha: {campaign['name']}. Cena atual: {scene_name}.")
    lines.append("")

    for i, p in enumerate(players):
        if i > 0:
            lines.append("---")
        pid = p["id"]
        state = player_states.get(pid, {})
        parts = [f"{p['name']}"]
        if p["is_gm"]:
            parts[0] += " (GM)"
        elif p.get("is_delegate"):
            parts[0] += " (delegado)"
        parts[0] += ":"

        stress_list = state.get("stress", [])
        if stress_list:
            stress_strs = [
                f"{s['stress_type_name']} {die_label(s['die_size'])}"
                for s in stress_list
            ]
            parts.append(f"Stress {', '.join(stress_strs)}.")
        else:
            parts.append("Sem stress.")

        trauma_list = state.get("trauma", [])
        if trauma_list:
            trauma_strs = [
                f"{t['stress_type_name']} {die_label(t['die_size'])}"
                for t in trauma_list
            ]
            parts.append(f"Trauma {', '.join(trauma_strs)}.")

        assets_list = state.get("assets", [])
        if assets_list:
            asset_strs = [
                f"{a['name']} {die_label(a['die_size'])} ({a['duration']})"
                for a in assets_list
            ]
            parts.append(f"Assets: {', '.join(asset_strs)}.")

        complications_list = state.get("complications", [])
        if complications_list:
            comp_strs = [
                f"{c['name']} {die_label(c['die_size'])}"
                for c in complications_list
            ]
            parts.append(f"Complications: {', '.join(comp_strs)}.")

        hero_list = state.get("hero_dice", [])
        if hero_list:
            hero_strs = [die_label(h["die_size"]) for h in hero_list]
            parts.append(f"Hero dice: {', '.join(hero_strs)}.")

        parts.append(f"PP {p['pp']}, XP {p['xp']}.")
        lines.append(" ".join(parts))

    if doom_pool is not None:
        if doom_pool:
            doom_strs = [die_label(d["die_size"]) for d in doom_pool]
            lines.append(f"\nDoom Pool: {', '.join(doom_strs)}.")
        else:
            lines.append("\nDoom Pool: vazio.")

    if scene_assets:
        asset_strs = [
            f"{a['name']} {die_label(a['die_size'])}"
            for a in scene_assets
        ]
        lines.append(f"Assets de cena: {', '.join(asset_strs)}.")

    if scene_complications:
        comp_strs = [
            f"{c['name']} {die_label(c['die_size'])}"
            for c in scene_complications
        ]
        lines.append(f"Complications de cena: {', '.join(comp_strs)}.")

    if crisis_pools:
        for cp in crisis_pools:
            dice_strs = [die_label(d["die_size"]) for d in cp.get("dice", [])]
            lines.append(f"Crisis Pool '{cp['name']}': {', '.join(dice_strs)}.")

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
    label = scene_name or "sem nome"
    lines.append(f"Cena encerrada: {label}.")

    if removed_assets:
        lines.append("Assets removidos:")
        for a in removed_assets:
            owner = a.get("player_name", "cena")
            lines.append(f"  {a['name']} {die_label(a['die_size'])} ({owner}).")

    if removed_complications:
        lines.append("Complications removidas:")
        for c in removed_complications:
            owner = c.get("player_name", "cena")
            lines.append(f"  {c['name']} {die_label(c['die_size'])} ({owner}).")

    if removed_crisis_pools:
        lines.append("Crisis pools removidos:")
        for cp in removed_crisis_pools:
            lines.append(f"  {cp['name']}.")

    if stress_changes:
        lines.append("Mudancas de stress (bridge):")
        for sc in stress_changes:
            if sc.get("eliminated"):
                lines.append(f"  {sc['player']}: {sc['type']} eliminado (era d4).")
            else:
                lines.append(
                    f"  {sc['player']}: {sc['type']} "
                    f"{die_label(sc['from'])} para {die_label(sc['to'])}."
                )

    if not (removed_assets or removed_complications or removed_crisis_pools):
        lines.append("Nenhum elemento de cena para remover.")

    if persistent_state:
        lines.append(f"\n{persistent_state}")

    return "\n".join(lines)


def format_action_confirm(action: str, details: str, player_state: str = "") -> str:
    msg = f"{action}. {details}"
    if player_state:
        msg += f" {player_state}"
    return msg
