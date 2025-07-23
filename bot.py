import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} が起動しました！")

async def main():
    await bot.load_extension("cogs.phase_controller")
    await bot.start(os.getenv("TOKEN"))  # または config.pyからTOKEN読み込み

asyncio.run(main())
