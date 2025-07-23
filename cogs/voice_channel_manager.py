import discord
from discord.ext import commands

class VoiceChannelManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="create_vcs")
    @commands.has_permissions(manage_channels=True)
    async def create_vcs(self, ctx, category: discord.CategoryChannel, *, names: str):
        """
        指定したカテゴリに複数のVCを作成するコマンド
        使い方例:
          !create_vcs カテゴリ名 VC1 VC2 VC3
        """
        # names はスペース区切りで複数VC名が入る想定
        vc_names = names.split()
        created_channels = []

        for name in vc_names:
            # カテゴリ内に同名のVCがないか確認
            existing = discord.utils.get(category.voice_channels, name=name)
            if existing:
                await ctx.send(f"既に同名のVCがカテゴリ内に存在します: {name}")
                continue
            vc = await category.create_voice_channel(name)
            created_channels.append(vc)

        if created_channels:
            created_names = ", ".join(vc.name for vc in created_channels)
            await ctx.send(f"以下のVCを作成しました:\n{created_names}")
        else:
            await ctx.send("新規作成されたVCはありませんでした。")

async def setup(bot):
    await bot.add_cog(VoiceChannelManager(bot))
