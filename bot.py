import discord
from discord.ext import commands
import asyncio

# Botのプレフィックスはスラッシュコマンドをメインに使うので最低限設定
intents = discord.Intents.default()
intents.message_content = True  # 必要に応じて

bot = commands.Bot(command_prefix="!", intents=intents)

# Cog群のファイル名リスト
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
    "helpme"  # 先ほど作成したHelpMe Cog
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    # スラッシュコマンドを同期（サーバーごとに同期を細かく調整可能）
    await bot.tree.sync()
    print("Slash commands synced.")

async def main():
    # Cogを一括ロード
    for cog in COG_LIST:
        try:
            await bot.load_extension(f"cogs.{cog}")
            print(f"Loaded cog: {cog}")
        except Exception as e:
            print(f"Failed to load cog {cog}: {e}")

    # Botトークンは環境変数や外部管理推奨
    TOKEN = "YOUR_BOT_TOKEN_HERE"
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
