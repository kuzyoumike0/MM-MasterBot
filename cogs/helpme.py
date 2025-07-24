import discord
from discord.ext import commands

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.command_attrs['help'] = "Botのすべてのコマンドを表示します。"

    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = discord.Embed(
            title="📘 ヘルプメニュー",
            description="このBotで使用可能なコマンド一覧です。\n`!コマンド名`で使用できます。",
            color=discord.Color.blue()
        )
        for cog, commands_list in mapping.items():
            filtered = await self.filter_commands(commands_list, sort=True)
            if filtered:
                cog_name = getattr(cog, "qualified_name", "その他")
                command_descriptions = [
                    f"`{self.context.clean_prefix}{cmd.name}`: {cmd.help or '説明なし'}"
                    for cmd in filtered
                ]
                embed.add_field(
                    name=f"📂 {cog_name}",
                    value="\n".join(command_descriptions),
                    inline=False
                )
        embed.set_footer(text="詳細は !help <コマンド名> を入力してください")
        await ctx.send(embed=embed)

    async def send_command_help(self, command):
        ctx = self.context
        embed = discord.Embed(
            title=f"ℹ️ コマンド: {command.name}",
            description=command.help or "説明が登録されていません。",
            color=discord.Color.green()
        )
        if command.aliases:
            embed.add_field(name="エイリアス", value=", ".join(command.aliases), inline=False)
        embed.add_field(name="使い方", value=f"`{self.context.clean_prefix}{command.name} {command.signature}`", inline=False)
        await ctx.send(embed=embed)

    async def send_error_message(self, error):
        await self.context.send(f"❌ エラー: {error}")

class HelpCog(commands.Cog, name="Help"):
    def __init__(self, bot):
        self.bot = bot
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
