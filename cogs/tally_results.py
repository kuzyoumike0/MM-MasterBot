import discord
from discord.ext import commands
from collections import defaultdict
import json
import os

DATA_FILE = "tally_data.json"

class TallyResults(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tally_data = defaultdict(list)
        self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.tally_data = json.load(f)

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tally_data, f, indent=2, ensure_ascii=False)

    @commands.command(name="add_vote")
    async def add_vote(self, ctx, category: str, *, vote: str):
        """集計データに投票を追加します。例: !add_vote 好きなキャラ 鈴木"""
        self.tally_data.setdefault(category, []).append(vote)
        self.save_data()
        await ctx.send(f"✅ {ctx.author.display_name} の投票を追加しました。")

    @commands.command(name="show_results")
    async def show_results(self, ctx, *, category: str):
        """指定カテゴリの投票結果を集計して表示します。例: !show_results 好きなキャラ"""
        if category not in self.tally_data:
            return await ctx.send("⚠️ 指定されたカテゴリは存在しません。")

        votes = self.tally_data[category]
        result_count = defaultdict(int)
        for v in votes:
            result_count[v] += 1

        sorted_results = sorted(result_count.items(), key=lambda x: x[1], reverse=True)

        result_msg = f"📊 **「{category}」の投票結果**\n"
        for i, (option, count) in enumerate(sorted_results, start=1):
            result_msg += f"{i}. {option}: {count}票\n"

        await ctx.send(result_msg)

    @commands.command(name="reset_results")
    @commands.has_permissions(administrator=True)
    async def reset_results(self, ctx, *, category: str):
        """指定カテゴリの集計結果をリセットします（管理者専用）"""
        if category in self.tally_data:
            del self.tally_data[category]
            self.save_data()
            await ctx.send(f"🗑️ 「{category}」の集計をリセットしました。")
        else:
            await ctx.send("⚠️ 指定されたカテゴリは存在しません。")

async def setup(bot):
    await bot.add_cog(TallyResults(bot))
