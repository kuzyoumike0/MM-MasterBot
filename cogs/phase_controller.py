import discord
from discord.ext import commands
import json
import os

PHASE_FILE = "data/phase_state.json"

# フェーズの定義（順番あり）
PHASES = [
    "導入",
    "自己紹介",
    "探索フェーズ",
    "議論フェーズ",
    "投票フェーズ",
    "エンディング"
]

def save_phase(guild_id, phase):
    os.makedirs(os.path.dirname(PHASE_FILE), exist_ok=True)
    try:
        with open(PHASE_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    data[str(guild_id)] = phase
    with open(PHASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_phase(guild_id):
    try:
        with open(PHASE_FILE, 'r') as f:
            data = json.load(f)
            return data.get(str(guild_id), None)
    except FileNotFoundError:
        return None


class PhaseController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_phase")
    async def set_phase(self, ctx, *, phase: str):
        """現在のフェーズを設定します"""
        if phase not in PHASES:
            await ctx.send(f"無効なフェーズです。有効なフェーズ: {', '.join(PHASES)}")
            return

        save_phase(ctx.guild.id, phase)
        await ctx.send(embed=discord.Embed(
            title="📘 現在のフェーズ",
            description=f"**{phase}** フェーズに移行しました。",
            color=discord.Color.blue()
        ))

    @commands.command(name="get_phase")
    async def get_phase(self, ctx):
        """現在のフェーズを確認します"""
        phase = load_phase(ctx.guild.id)
        if phase:
            await ctx.send(f"現在のフェーズは **{phase}** です。")
        else:
            await ctx.send("フェーズがまだ設定されていません。")

    @commands.command(name="next_phase")
    async def next_phase(self, ctx):
        """フェーズを次に進めます"""
        current = load_phase(ctx.guild.id)
        if current not in PHASES:
            next_phase = PHASES[0]
        else:
            idx = PHASES.index(current)
            next_phase = PHASES[idx + 1] if idx + 1 < len(PHASES) else PHASES[-1]

        save_phase(ctx.guild.id, next_phase)
        await ctx.send(embed=discord.Embed(
            title="📘 フェーズ進行",
            description=f"フェーズが **{next_phase}** に進みました。",
            color=discord.Color.green()
        ))

async def setup(bot):
    await bot.add_cog(PhaseController(bot))
