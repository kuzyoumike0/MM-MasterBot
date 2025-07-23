import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
import pytz

class ScheduledMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduled_tasks = []

    @commands.command(name="schedule_message")
    @commands.has_permissions(manage_messages=True)
    async def schedule_message(
        self,
        ctx,
        channel: discord.TextChannel,
        datetime_str: str,
        *,
        message: str
    ):
        """
        指定した日時にメッセージを送信します。
        使用例:
          !schedule_message #通知チャンネル 2025-07-24T21:00:00 まもなくイベントが始まります！
        （※日時は ISO 8601形式: YYYY-MM-DDTHH:MM:SS）
        """
        try:
            # JSTに変換（例: UTC+9）
            jst = pytz.timezone("Asia/Tokyo")
            scheduled_dt = datetime.fromisoformat(datetime_str)
            if scheduled_dt.tzinfo is None:
                scheduled_dt = jst.localize(scheduled_dt)

            now = datetime.now(jst)
            delay = (scheduled_dt - now).total_seconds()

            if delay <= 0:
                await ctx.send("指定された時間はすでに過ぎています。未来の日時を指定してください。")
                return

            await ctx.send(f"{channel.mention} に {scheduled_dt.strftime('%Y-%m-%d %H:%M:%S')} にメッセージを送信予定です。")

            # 非同期タスクでスケジュール
            self.bot.loop.create_task(self._delayed_send(channel, message, delay))

        except Exception as e:
            await ctx.send(f"エラー: {e}\n日時は `YYYY-MM-DDTHH:MM:SS` 形式で指定してください。")

    async def _delayed_send(self, channel, message, delay):
        await asyncio.sleep(delay)
        await channel.send(message)

async def setup(bot):
    await bot.add_cog(ScheduledMessage(bot))
