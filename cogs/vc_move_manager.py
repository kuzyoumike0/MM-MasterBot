import discord
from discord.ext import commands

class VCMoveManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="move_to_vc")
    @commands.has_permissions(move_members=True)
    async def move_to_vc(self, ctx, target_vc: discord.VoiceChannel, *, source_vcs: str):
        """
        複数のボイスチャンネルから参加者をまとめて指定のVCに移動させるコマンド

        使い方例:
          !move_to_vc 移動先VC名 or ID ソースVC1,ソースVC2,ソースVC3

        - target_vc : 移動先のVC（名前またはIDで指定）
        - source_vcs : カンマ区切りで移動元VC名を複数指定

        """
        guild = ctx.guild
        moved_members = []
        failed_members = []

        source_vc_names = [name.strip() for name in source_vcs.split(",") if name.strip()]

        # ソースVCリストを取得
        source_channels = []
        for name in source_vc_names:
            ch = discord.utils.get(guild.voice_channels, name=name)
            if ch:
                source_channels.append(ch)
            else:
                await ctx.send(f"ボイスチャンネルが見つかりません: {name}")
                return

        # 対象VCがguildにあるかチェック
        if target_vc.guild != guild:
            await ctx.send("移動先のVCがこのサーバーに存在しません。")
            return

        for vc in source_channels:
            for member in vc.members:
                try:
                    await member.move_to(target_vc)
                    moved_members.append(member.display_name)
                except Exception:
                    failed_members.append(member.display_name)

        msg = f"移動成功: {len(moved_members)}人\n"
        if moved_members:
            msg += "移動済みメンバー: " + ", ".join(moved_members) + "\n"
        if failed_members:
            msg += "移動失敗メンバー: " + ", ".join(failed_members)
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(VCMoveManager(bot))
