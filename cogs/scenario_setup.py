import discord
from discord.ext import commands

class ScenarioSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup_scenario")
    @commands.has_permissions(manage_roles=True, manage_channels=True)
    async def setup_scenario(self, ctx, scenario_name: str):
        """
        シナリオ用ロールとプライベートチャンネルを作成します。
        使用例: !setup_scenario 鬼火村の惨劇
        """
        guild = ctx.guild

        # ロール作成
        role = discord.utils.get(guild.roles, name=scenario_name)
        if not role:
            role = await guild.create_role(name=scenario_name)
            await ctx.send(f"ロール `{scenario_name}` を作成しました。")
        else:
            await ctx.send(f"ロール `{scenario_name}` は既に存在します。")

        # カテゴリ作成（なければ）
        category = discord.utils.get(guild.categories, name="シナリオ用")
        if not category:
            category = await guild.create_category("シナリオ用")

        # テキストチャンネル作成
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
        }
        channel_name = scenario_name.replace(" ", "-").lower()
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)

        if existing_channel:
            await ctx.send(f"チャンネル `{channel_name}` は既に存在します。")
        else:
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)
            await ctx.send(f"チャンネル <#{channel.id}> を作成しました。")

async def setup(bot):
    await bot.add_cog(ScenarioSetup(bot))
