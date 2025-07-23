import discord
from discord.ext import commands

class BulkNicknameSetter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_nicknames")
    @commands.has_permissions(manage_nicknames=True)
    async def set_nicknames(self, ctx, *, data: str):
        """
        複数ユーザーのニックネームを一括で設定します。

        使用例:
        !set_nicknames
        @user1 ニックネーム1
        @user2 ニックネーム2

        ※ 改行で区切って複数入力可能。
        """
        lines = data.strip().split("\n")
        success = []
        failed = []

        for line in lines:
            parts = line.strip().split(maxsplit=1)
            if len(parts) != 2:
                failed.append(f"形式エラー: `{line}`")
                continue

            mention, nickname = parts
            try:
                member = await commands.MemberConverter().convert(ctx, mention)
                await member.edit(nick=nickname)
                success.append(f"{member.display_name} → {nickname}")
            except Exception as e:
                failed.append(f"{mention}: {str(e)}")

        result = "**✅ ニックネーム変更結果**\n"
        if success:
            result += "\n**成功:**\n" + "\n".join(success)
        if failed:
            result += "\n**失敗:**\n" + "\n".join(failed)

        await ctx.send(result)

async def setup(bot):
    await bot.add_cog(BulkNicknameSetter(bot))
