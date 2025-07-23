import discord
from discord.ext import commands
import asyncio
import os

# 必要なIntentsを設定（用途に応じて調整してください）
intents = discord.Intents.default()
intents.message_content = True  # メッセージコンテンツを扱う場合に必要

bot = commands.Bot(command_prefix="!", intents=intents)

# 読み込むCogのリスト（cogsフォルダ内にある各Cogのファイル名から拡張子なしで指定）
COG_MODULES = [
    "auth_role",
    "bulk_message_sender",
    "bulk_nickname_setter",
    "delete_category",
    "dice_roller",
    "generic_button_vote",
    "phase_controller",
    "private_text_channels",
    "progress_bot",
    "reminder_bot",
    "scenario_modifier",
    "scenario_setup",
    "scheduled_message",
    "summary_bot",
    "vc_move_manager",
    "voice_channel_manager",
    "helpme"  # HelpMe Cog
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.tree.sync()
    print("Slash commands synced.")

async def load_cogs():
    for cog in COG_MODULES:
        try:
            await bot.load_extension(f"cogs.{cog}")
            print(f"Loaded cog: {cog}")
        except Exception as e:
            print(f"Error loading cog {cog}: {e}")

async def main():
    await load_cogs()
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN 環境変数が設定されていません。")
        return
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
