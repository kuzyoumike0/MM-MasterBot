import discord
from discord.ext import commands

class ScenarioModifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add_to_scenario")
    @commands.has_permissions(manage_roles=True)
    async def add_to_scenario(self, ctx, role_name: str, member: discord.Member):
        """
        指定されたロール（シナリオ）にメンバーを追加し、対応チャンネルの閲覧権限も付与。
        使用例: !add_to_scenario 鬼火村の惨劇 @プレイヤー
        """
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            await ctx.send(f"ロール `{role_name}` が見つかりません。")
            return

        await member.add_roles(role)
        await ctx.send(f"{member.mention} を `{role_name}` に追加しました。")

        # 関連チャンネルにも権限を付与
        for channel in guild.text_channels:
            if role_name.replace(" ", "-").lower() in channel.name:
                try:
                    await channel.set_permissions(member, read_messages=True, send_messages=True)
                except discord.Forbidden:
                    await ctx.send(f"チャンネル `{channel.name}` へのパーミッション設定に失敗しました。")

    @commands.command(name="remove_from_scenario")
    @commands.has_permissions(manage_roles=True)
    async def remove_from_scenario(self, ctx, role_name: str, member: discord.Member):
        """
        指定されたロールからメンバーを削除し、チャンネルの閲覧も削除。
        使用例: !remove_from_scenario 鬼火村の惨劇 @プレイヤー
        """
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            await ctx.send(f"ロール `{role_name}` が見つかりません。")
            return

        await member.remove_roles(role)
        await ctx.send(f"{member.mention} を `{role_name}` から削除しました。")

        # 関連チャンネルのパーミッションも解除
        for channel in guild.text_channels:
            if role_name.replace(" ", "-").lower() in channel.name:
                try:
                    await channel.set_permissions(member, overwrite=None)
                except discord.Forbidden:
                    await ctx.send(f"チャンネル `{channel.name}` の権限解除に失敗しました。")

    @commands.command(name="rename_scenario_channel")
    @commands.has_permissions(manage_channels=True)
    async def rename_scenario_channel(self, ctx, old_name: str, new_name: str):
        """
        シナリオ用チャンネルの名前を変更します。
        使用例: !rename_scenario_channel 鬼火村の惨劇 新・鬼火村編
        """
        guild = ctx.guild
        old_channel = discord.utils.get(guild.text_channels, name=old_name.replace(" ", "-").lower())
        if not old_channel:
            await ctx.send(f"チャンネル `{old_name}` が見つかりません。")
            return

        try:
            await old_channel.edit(name=new_name.replace(" ", "-").lower())
            await ctx.send(f"チャンネル名を `{old_name}` → `{new_name}` に変更しました。")
        except discord.Forbidden:
            await ctx.send("チャンネル名の変更に失敗しました。権限を確認してください。")

async def setup(bot):
    await bot.add_cog(ScenarioModifier(bot))
