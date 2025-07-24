# bot.py
import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# .envファイルから環境変数をロード（無ければスキップ）
try:
    load_dotenv()
except Exception:
    print("[⚠️] dotenvが読み込めません。環境変数が直接設定されているか確認してください。")

# DISCORD_BOT_TOKEN を環境変数から取得
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 全Intentsを有効化（音声・ステータス・DM・リアクション・メッセージ等）
intents = discord.Intents.all()

# Botインスタンス作成
bot = commands.Bot(command_prefix="!", intents=intents)

# Cogファイル（cogsディレクトリ内の.pyファイル名から拡張子を除いたもの）
COG_LIST = [
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
    "helpme"
]

@bot.event
async def on_ready():
    print(f"[✅] Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"[🌐] Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"[⚠️] Failed to sync slash commands: {e}")

async def load_all_cogs():
    for cog in COG_LIST:
        try:
            await bot.load_extension(f"cogs.{cog}")
            print(f"[🔧] Loaded cog: {cog}")
        except Exception as e:
            print(f"[❌] Failed to load cog '{cog}': {e}")

async def start_bot():
    global TOKEN
    # トークンが設定されていない場合は起動前に入力を促す
    if not TOKEN:
        print("[❗] DISCORD_BOT_TOKEN が環境変数に設定されていません。")
        TOKEN = input("🔐 Botのトークンを入力してください: ").strip()
        if not TOKEN:
            print("[❌] トークンが入力されなかったため、起動を中止します。")
            return

    await load_all_cogs()
    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        print("[❌] Discord bot token が無効です。")
    except Exception as e:
        print(f"[❌] Bot起動中に予期せぬエラーが発生しました: {e}")

# 直接実行された場合（main.py とは別にスタンドアロン実行も可能）
if __name__ == "__main__":
    asyncio.run(start_bot())
