import discord
from discord.ext import commands
import asyncio

class RemoveLeftMemberMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="remove_left_messages")
    @commands.has_permissions(manage_messages=True)
    async def remove_left_messages(self, ctx, limit: int = 100):
        """
        サーバーから脱退したメンバーのメッセージを指定した数だけ削除します。
        limit: 各チャンネルで遡ってチェックするメッセージ数の上限（デフォルト100）
        使用例:
        !remove_left_messages 200
        """
        guild = ctx.guild
        if not guild:
            await ctx.send("このコマンドはサーバー内で実行してください。")
            return

        await ctx.send(f"脱退メンバーのメッセージ削除を開始します。各テキストチャンネルの過去{limit}件を対象にします。")

        # 現在サーバーにいないユーザーIDの集合
        current_member_ids = {member.id for member in guild.members}

        deleted_count_total = 0

        for channel in guild.text_channels:
            def is_left_author(m):
                return m.author and m.author.id not in current_member_ids

            deleted_count = 0
            try:
                async for message in channel.history(limit=limit):
                    if is_left_author(message):
                        await message.delete()
                        deleted_count += 1
                        deleted_count_total += 1
                        # Discord API負荷対策で短い待機を入れる
                        await asyncio.sleep(0.5)
            except discord.Forbidden:
                await ctx.send(f"権限不足のため、{channel.name} のメッセージを削除できませんでした。")
            except Exception as e:
                await ctx.send(f"{channel.name} でエラーが発生しました: {e}")

            if deleted_count > 0:
                await ctx.send(f"{channel.name} で {deleted_count} 件のメッセージを削除しました。")

        await ctx.send(f"処理完了。合計 {deleted_count_total} 件のメッセージを削除しました。")

async def setup(bot):
    await bot.add_cog(RemoveLeftMemberMessages(bot))
