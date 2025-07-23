import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
from datetime import datetime, timedelta
import re

REMINDER_FILE = "data/reminders.json"

def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return []
    with open(REMINDER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_reminders(reminders):
    os.makedirs(os.path.dirname(REMINDER_FILE), exist_ok=True)
    with open(REMINDER_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, indent=4, ensure_ascii=False)

def parse_time(time_str: str) -> int:
    """
    "10m", "2h", "30s" 形式を秒数に変換
    """
    match = re.match(r"(\d+)([smhd])", time_str)
    if not match:
        return -1
    amount, unit = match.groups()
    amount = int(amount)
    if unit == "s":
        return amount
    elif unit == "m":
        return amount * 60
    elif unit == "h":
        return amount * 3600
    elif unit == "d":
        return amount * 86400
    return -1

class ReminderBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = load_reminders()
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    @tasks.loop(seconds=10)
    async def check_reminders(self):
        now = datetime.utcnow().timestamp()
        to_remove = []
        for r in self.reminders:
            if r["time"] <= now:
                user = self.bot.get_user(r["user_id"])
                if user:
                    try:
                        await user.send(f"⏰ リマインダー: {r['message']}")
                    except:
                        pass
                to_remove.append(r)
        if to_remove:
            for r in to_remove:
                self.reminders.remove(r)
            save_reminders(self.reminders)

    @commands.command()
    async def remind(self, ctx, time: str, *, message: str):
        """例: !remind 10m ご飯を食べる"""
        seconds = parse_time(time)
        if seconds < 0:
            await ctx.send("時間指定の形式が不正です。例: 10m, 2h, 30s")
            return
        remind_time = datetime.utcnow().timestamp() + seconds
        self.reminders.append({
            "user_id": ctx.author.id,
            "time": remind_time,
            "message": message
        })
        save_reminders(self.reminders)
        await ctx.send(f"{seconds}秒後にリマインドを設定しました。")

    @commands.command()
    async def reminders(self, ctx):
        """登録中のリマインダー一覧"""
        user_reminders = [r for r in self.reminders if r["user_id"] == ctx.author.id]
        if not user_reminders:
            return await ctx.send("リマインダーは登録されていません。")
        lines = []
        now = datetime.utcnow().timestamp()
        for i, r in enumerate(user_reminders, 1):
            remain = int(r["time"] - now)
            lines.append(f"{i}. {r['message']} （あと{remain}秒）")
        await ctx.send("📋 あなたのリマインダー一覧:\n" + "\n".join(lines))

    @commands.command()
    async def cancel_reminder(self, ctx, index: int):
        """リマインダーをキャンセル"""
        user_reminders = [r for r in self.reminders if r["user_id"] == ctx.author.id]
        if index < 1 or index > len(user_reminders):
            return await ctx.send("無効な番号です。")
        r = user_reminders[index - 1]
        self.reminders.remove(r)
        save_reminders(self.reminders)
        await ctx.send(f"リマインダー「{r['message']}」をキャンセルしました。")

async def setup(bot):
    await bot.add_cog(ReminderBot(bot))
