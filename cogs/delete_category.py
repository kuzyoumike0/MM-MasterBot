import discord
from discord.ext import commands

class DeleteCategory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="delete_category")
    @commands.has_permissions(manage_channels=True)
    async def delete_category(self, ctx, *, category_name: str):
        """
        指定したカテゴリとその中の全チャンネルを削除します。
        使用例: !delete_category ゲーム用カテゴリ
        """
        guild = ctx.guild
        category = discord.utils.get(guild.categories, name=category_name)

        if not category:
            await ctx.send(f"カテゴリ「{category_name}」が見つかりません。")
            return

        # カテゴリ内のチャンネルを削除
        for channel in category.channels:
            try:
                await channel.delete()
            except discord.Forbidden:
                await ctx.send(f"チャンネル {channel.name} の削除権限がありません。")

        # カテゴリ自体を削除
        try:
            await category.delete()
            await ctx.send(f"カテゴリ「{category_name}」とそのチャンネルを削除しました。")
        except discord.Forbidden:
            await ctx.send(f"カテゴリ「{category_name}」の削除権限がありません。")

async def setup(bot):
    await bot.add_cog(DeleteCategory(bot))
