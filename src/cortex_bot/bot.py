import asyncio
import logging

import discord
from discord.ext import commands

from cortex_bot.config import settings
from cortex_bot.models.database import Database

log = logging.getLogger("cortex_bot")

COGS = [
    "cortex_bot.cogs.campaign",
    "cortex_bot.cogs.scene",
    "cortex_bot.cogs.state",
    "cortex_bot.cogs.rolling",
    "cortex_bot.cogs.doom",
    "cortex_bot.cogs.undo",
]


class CortexBot(commands.Bot):
    def __init__(self, db: Database) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.db = db

    async def setup_hook(self) -> None:
        await self.db.initialize()
        for cog in COGS:
            await self.load_extension(cog)
        await self.tree.sync()

    async def on_ready(self) -> None:
        log.info("Bot ready as %s", self.user)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    token = settings.token.get_secret_value()
    if not token:
        raise RuntimeError("CORTEX_BOT_TOKEN environment variable not set")

    db = Database()
    bot = CortexBot(db)
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
