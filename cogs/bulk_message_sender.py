import discord
from discord.ext import commands
import os

class BulkMessageSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bulk_send_text")
    @commands.has_permissions(manage_channels=True)
    async def bulk_send_text(self, ctx, *, channel_names_and_message: str):
        """
        指定した複数のテキストチャンネルに同じメッセージを送信します。

        使い方例:
          !bulk_send_text channel1,channel2,channel3|メッセージ内容

        「,」区切りでチャンネル名リストと「|」で区切ってメッセージを指定してください。
        """
        try:
            channels_part, message = channel_names_and_message.split("|", maxsplit=1)
            channel_names = [name.strip() for name in channels_part.split(",") if name.strip()]
        except Exception:
            await ctx.send("形式が正しくありません。例: `!bulk_send_text channel1,channel2|こんにちは`")
            return

        sent_channels = []
        failed_channels = []

        for name in channel_names:
            channel = discord.utils.get(ctx.guild.text_channels, name=name)
            if channel:
                try:
                    await channel.send(message)
                    sent_channels.append(name)
                except Exception:
                    failed_channels.append(name)
            else:
                failed_channels.append(name)

        result_msg = f"送信完了: {len(sent_channels)} チャンネル\n"
        if sent_channels:
            result_msg += "送信成功チャンネル: " + ", ".join(sent_channels) + "\n"
        if failed_channels:
            result_msg += "送信失敗チャンネルまたは存在しないチャンネル: " + ", ".join(failed_channels)

        await ctx.send(result_msg)

    @commands.command(name="bulk_send_file")
    @commands.has_permissions(manage_channels=True)
    async def bulk_send_file(self, ctx, channels: str, file_path: str):
        """
        指定した複数のテキストチャンネルに同じファイルを送信します。

        使い方例:
          !bulk_send_file channel1,channel2,channel3 path/to/file.png

        チャンネル名はカンマ区切り、ファイルパスはBotがアクセスできるローカルパスで指定してください。
        """
        channel_names = [name.strip() for name in channels.split(",") if name.strip()]

        if not os.path.exists(file_path):
            await ctx.send(f"ファイルが存在しません: {file_path}")
            return

        sent_channels = []
        failed_channels = []

        for name in channel_names:
            channel = discord.utils.get(ctx.guild.text_channels, name=name)
            if channel:
                try:
                    await channel.send(file=discord.File(file_path))
                    sent_channels.append(name)
                except Exception:
                    failed_channels.append(name)
            else:
                failed_channels.append(name)

        result_msg = f"ファイル送信完了: {len(sent_channels)} チャンネル\n"
        if sent_channels:
            result_msg += "送信成功チャンネル: " + ", ".join(sent_channels) + "\n"
        if failed_channels:
            result_msg += "送信失敗チャンネルまたは存在しないチャンネル: " + ", ".join(failed_channels)

        await ctx.send(result_msg)

async def setup(bot):
    await bot.add_cog(BulkMessageSender(bot))
