import discord
from discord.ext import commands
import json
import os

PROGRESS_FILE = "data/progress.json"

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {"progress": 0, "tasks": {}}
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_progress(data):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class ProgressBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_progress()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_progress(self, ctx, percent: int):
        """進捗をパーセンテージで設定"""
        if percent < 0 or percent > 100:
            return await ctx.send("0から100の間で指定してください。")
        self.data["progress"] = percent
        save_progress(self.data)
        await ctx.send(f"進捗を {percent}% に設定しました。")

    @commands.command()
    async def show_progress(self, ctx):
        """現在の進捗を表示"""
        p = self.data.get("progress", 0)
        bar_length = 20
        filled_len = int(bar_length * p // 100)
        bar = "█" * filled_len + "░" * (bar_length - filled_len)
        embed = discord.Embed(title="📊 進捗状況")
        embed.add_field(name="進捗率", value=f"{p}%")
        embed.add_field(name="進捗バー", value=bar)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_task(self, ctx, *, task_name: str):
        """タスクを追加"""
        if task_name in self.data["tasks"]:
            return await ctx.send("その名前のタスクは既にあります。")
        self.data["tasks"][task_name] = False
        save_progress(self.data)
        await ctx.send(f"タスク「{task_name}」を追加しました。")

    @commands.command()
    async def list_tasks(self, ctx):
        """タスク一覧表示"""
        tasks = self.data.get("tasks", {})
        if not tasks:
            return await ctx.send("タスクはまだありません。")
        lines = []
        for t, done in tasks.items():
            status = "✅" if done else "❌"
            lines.append(f"{status} {t}")
        await ctx.send("### タスク一覧 ###\n" + "\n".join(lines))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def complete_task(self, ctx, *, task_name: str):
        """タスク完了にする"""
        if task_name not in self.data["tasks"]:
            return await ctx.send("そのタスクは存在しません。")
        self.data["tasks"][task_name] = True
        save_progress(self.data)
        await ctx.send(f"タスク「{task_name}」を完了にしました。")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_progress(self, ctx):
        """進捗とタスクをリセット"""
        self.data = {"progress": 0, "tasks": {}}
        save_progress(self.data)
        await ctx.send("進捗とタスクをリセットしました。")

async def setup(bot):
    await bot.add_cog(ProgressBot(bot))
