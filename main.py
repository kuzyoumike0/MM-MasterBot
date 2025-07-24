# main.py
import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
import glob

# .envから環境変数を読み込む（存在しなくても続行）
try:
    load_dotenv()
except Exception:
    print("[⚠️] dotenvの読み込みに失敗しました。環境変数が直接設定されているか確認してください。")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Intents（必要に応じて調整可。Voice・DM・メッセージなど一通り有効化）
intents = discord.Intents.all()

# Bot本体
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[✅] Bot is ready: {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"[🌐] Slash commands synced ({len(synced)} commands).")
    except Exception as e:
        print(f"[⚠️] Slash command sync failed: {e}")

async def load_cogs():
    # cogsディレクトリ内の.pyファイルすべてを対象に
    cog_files = glob.glob("cogs/*.py")
    for file in cog_files:
        if file.endswith("__init__.py"):
            continue  # __init__.pyは除外
        cog_name = os.path.splitext(os.path.basename(file))[0]
        try:
            await bot.load_extension(f"cogs.{cog_name}")
            print(f"[🔧] Loaded cog: {cog_name}")
        except Exception as e:
            print(f"[❌] Failed to load cog '{cog_name}': {e}")

async def main():
    global TOKEN
    if not TOKEN:
        print("[❗] DISCORD_BOT_TOKEN が .env または環境変数に設定されていません。")
        print("環境変数にトークンをセットしてから再起動してください。")
        return

    await load_cogs()

    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        print("[❌] Bot Tokenが無効です。正しいトークンを設定してください。")
    except Exception as e:
        print(f"[❌] Bot起動時にエラーが発生しました: {e}")

if __name__ == "__main__":
    asyncio.run(main())
