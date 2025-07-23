import discord
from discord.ext import commands
import re
import random

DICE_PATTERN = re.compile(r"(\d*)d(\d+)([+-]\d+)?")

class DiceRoller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll", aliases=["dice", "r"])
    async def roll_dice(self, ctx, *, expression: str = "1d100"):
        """
        ダイスロールコマンド（例: !roll 1d100、!roll 2d6+3、!roll 3d10-2）
        """
        match = DICE_PATTERN.fullmatch(expression.replace(" ", ""))
        if not match:
            return await ctx.send("❌ フォーマットが正しくありません。例: `1d100`、`2d6+3`")

        num_dice = int(match.group(1)) if match.group(1) else 1
        dice_sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        if num_dice > 100 or dice_sides > 1000:
            return await ctx.send("❌ ダイスの数または面数が大きすぎます。（100個以下、面数1000以下）")

        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        modifier_str = f"{'+' if modifier >= 0 else ''}{modifier}" if modifier != 0 else ""

        result_str = f"🎲 {ctx.author.display_name} のロール: `{expression}`\n"
        result_str += f"出目: {rolls} {modifier_str}\n"
        result_str += f"🧮 合計: **{total}**"

        await ctx.send(result_str)

async def setup(bot):
    await bot.add_cog(DiceRoller(bot))
