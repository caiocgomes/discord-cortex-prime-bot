"""Discord UI views for the Cortex bot."""

from cortex_bot.views.base import CortexView, parse_custom_id, make_custom_id


def register_persistent_views(bot) -> None:
    """Register all persistent views and DynamicItems with the bot.

    Must be called in setup_hook before loading cogs.
    """
    from cortex_bot.views.common import UndoButton, CampaignInfoButton
    from cortex_bot.views.scene_views import SceneStartButton
    from cortex_bot.views.rolling_views import RollStartButton
    from cortex_bot.views.state_views import (
        StressAddStartButton,
        AssetAddStartButton,
        ComplicationAddStartButton,
        PPStartButton,
        XPStartButton,
    )
    from cortex_bot.views.doom_views import DoomAddStartButton

    bot.add_dynamic_items(
        UndoButton,
        CampaignInfoButton,
        SceneStartButton,
        RollStartButton,
        StressAddStartButton,
        AssetAddStartButton,
        ComplicationAddStartButton,
        PPStartButton,
        XPStartButton,
        DoomAddStartButton,
    )
