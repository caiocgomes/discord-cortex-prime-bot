"""Help command with contextual topic variants."""

import logging

from discord import app_commands, Interaction
from discord.ext import commands

log = logging.getLogger(__name__)

HELP_GENERAL = (
    "Cortex Bot: session manager for Cortex Prime RPG.\n"
    "\n"
    "Core lifecycle: /campaign setup to create a campaign, "
    "/scene start to begin a scene, /roll to roll dice.\n"
    "\n"
    "Command groups:\n"
    "- /campaign: create, end, view campaign info, delegate\n"
    "- /scene: start, end, view scene info\n"
    "- /roll: roll dice with assets and extras\n"
    "- /gmroll: GM/NPC roll without personal state\n"
    "- /asset: add, step up, step down, remove assets\n"
    "- /stress: add, step up, step down, remove stress\n"
    "- /complication: add, step up, step down, remove complications\n"
    "- /pp: add and spend plot points\n"
    "- /xp: add and remove experience points\n"
    "- /doom: doom pool (if enabled)\n"
    "- /crisis: crisis pools (if enabled)\n"
    "- /hero: hero dice (if enabled)\n"
    "- /trauma: trauma (if enabled)\n"
    "- /undo: undo last action\n"
    "\n"
    "Use /help topic:gm for GM commands, "
    "/help topic:player for player commands, "
    "/help topic:rolling for dice reference."
)

HELP_GM = (
    "GM commands, organized by phase.\n"
    "\n"
    "Campaign setup:\n"
    "- /campaign setup name:\"Name\" players:@Alice @Bob stress_types:\"Physical,Mental\"\n"
    "  Creates a campaign in this channel. You become the GM automatically.\n"
    "- /campaign delegate player:@Alice - promote a player to delegate\n"
    "- /campaign undelegate player:@Alice - revoke delegation\n"
    "\n"
    "During a scene:\n"
    "- /stress add player:@Alice type:Physical die:d8 - add stress\n"
    "- /stress stepup player:@Alice type:Physical - step up stress\n"
    "- /complication add name:\"On Fire\" die:d6 player:@Alice - create complication\n"
    "- /asset add name:\"Cover\" die:d8 scene_asset:True - create scene asset\n"
    "- /doom add die:d6 - add die to doom pool (if Doom Pool is enabled)\n"
    "- /doom roll - roll the doom pool\n"
    "- /gmroll dice:2d8 1d10 - roll as GM/NPC\n"
    "\n"
    "Between scenes:\n"
    "- /scene start name:\"Tavern Fight\" - start a new scene\n"
    "- /scene end - end scene (removes scene assets and complications)\n"
    "- /scene end bridge:True - bridge scene: step down all stress\n"
    "\n"
    "Administration:\n"
    "- /campaign end confirm:yes - end campaign permanently\n"
    "- /campaign info - view full state\n"
    "- /undo - undo last action (GM can undo any player's action)"
)

HELP_PLAYER = (
    "Player commands.\n"
    "\n"
    "Rolling:\n"
    "- /roll dice:1d8 1d10 1d6 - roll a dice pool\n"
    "- /roll dice:1d8 1d10 include:\"Big Wrench\" - include an asset in the pool\n"
    "- /roll dice:1d8 1d10 extra:1d6 - buy extra dice with PP (costs 1 PP per die)\n"
    "- /roll dice:1d8 1d10 difficulty:12 - roll against a difficulty\n"
    "\n"
    "Assets:\n"
    "- /asset add name:\"Big Wrench\" die:d6 - create an asset for yourself\n"
    "- /asset stepup name:\"Big Wrench\" - step up the asset\n"
    "- /asset stepdown name:\"Big Wrench\" - step down the asset\n"
    "- /asset remove name:\"Big Wrench\" - remove the asset\n"
    "\n"
    "Plot Points:\n"
    "- /pp add amount:1 - gain PP\n"
    "- /pp remove amount:1 - spend PP\n"
    "\n"
    "Complications:\n"
    "- /complication add name:\"Broken Arm\" die:d6 - create a complication\n"
    "- /complication stepdown name:\"Broken Arm\" - step down\n"
    "\n"
    "Information:\n"
    "- /campaign info - view campaign state and your data\n"
    "- /scene info - view current scene state"
)

HELP_ROLLING = (
    "Cortex Prime rolling reference.\n"
    "\n"
    "Dice notation: use dX or NdX where X is 4, 6, 8, 10, or 12.\n"
    "Examples: d8, 1d10, 2d6. Separate dice with spaces: 1d8 1d10 2d6.\n"
    "\n"
    "Include: add assets to the pool by name.\n"
    "Example: /roll dice:1d8 1d10 include:\"Sword\"\n"
    "The asset die is added to the pool automatically.\n"
    "\n"
    "Extra: buy extra dice by spending PP (1 PP per die).\n"
    "Example: /roll dice:1d8 1d10 extra:1d6\n"
    "\n"
    "Difficulty: compare the total against a target number.\n"
    "Example: /roll dice:1d8 1d10 difficulty:10\n"
    "Result shows success (margin) or failure (how much was missing).\n"
    "\n"
    "Hitches: dice that roll 1 are hitches. They do not count toward the total.\n"
    "GM may award 1 PP and create a d6 complication, or add dice to the Doom Pool.\n"
    "\n"
    "Botch: if all dice roll 1, it is a botch. Total is zero.\n"
    "GM creates a free d6 complication, stepped up per additional hitch.\n"
    "\n"
    "Best mode: when enabled, the bot calculates the best combinations of 2 dice.\n"
    "Shows best total and best effect die as pre-calculated options.\n"
    "\n"
    "Effect die: the third highest die (not used in the total) defines the effect die.\n"
    "If there is no third die, default is d4.\n"
    "\n"
    "Heroic success: margin of 5+ over the difficulty.\n"
    "Effect die steps up once for every 5 points of margin."
)

HELP_TOPICS = {
    "general": HELP_GENERAL,
    "gm": HELP_GM,
    "player": HELP_PLAYER,
    "rolling": HELP_ROLLING,
}


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="help", description="Bot command reference.")
    @app_commands.describe(topic="Help topic")
    @app_commands.choices(
        topic=[
            app_commands.Choice(name="General", value="general"),
            app_commands.Choice(name="GM", value="gm"),
            app_commands.Choice(name="Player", value="player"),
            app_commands.Choice(name="Rolling", value="rolling"),
        ],
    )
    async def help_command(
        self,
        interaction: Interaction,
        topic: app_commands.Choice[str] | None = None,
    ) -> None:
        key = topic.value if topic else "general"
        text = HELP_TOPICS[key]

        # Attach MenuButton if there's an active campaign in this channel
        view = None
        db = interaction.client.db
        campaign = await db.get_campaign(
            str(interaction.guild_id), str(interaction.channel_id)
        )
        if campaign:
            from cortex_bot.views.common import MenuOnlyView

            view = MenuOnlyView(campaign["id"])

        await interaction.response.send_message(text, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
