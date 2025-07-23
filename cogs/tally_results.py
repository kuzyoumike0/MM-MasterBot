import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from typing import List, Dict
import asyncio

class VoteButton(Button):
    def __init__(self, label: str, vote_id: str, bot, vote_data: dict):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.vote_id = vote_id
        self.bot = bot
        self.vote_data = vote_data
        self.choice = label

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        # ユーザーがすでに投票しているか確認
        if user_id in self.vote_data[self.vote_id]["votes"]:
            await interaction.response.send_message("すでに投票しています。", ephemeral=True)
            return

        # 投票記録
        self.vote_data[self.vote_id]["votes"][user_id] = self.choice
        await interaction.response.send_message(f"「{self.choice}」に投票しました。", ephemeral=True)

class VoteView(View):
    def __init__(self, options: List[str], vote_id: str, bot, vote_data: dict, timeout=600):
        super().__init__(timeout=timeout)
        for option in options:
            self.add_item(VoteButton(option, vote_id, bot, vote_data))

class ButtonVote(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vote_data: Dict[str, dict] = {}  # {vote_id: {"question": str, "options": [str], "votes": {user_id: choice}}}
        self.vote_counter = 0

    @app_commands.command(name="start_vote", description="ボタンで投票を開始する")
    @app_commands.describe(question="投票の質問", options="選択肢（カンマ区切り）")
    async def start_vote(self, interaction: discord.Interaction, question: str, options: str):
        opts = [opt.strip() for opt in options.split(",") if opt.strip()]
        if len(opts) < 2:
            await interaction.response.send_message("選択肢は2つ以上必要です。", ephemeral=True)
            return

        self.vote_counter += 1
        vote_id = f"vote_{self.vote_counter}"

        # 投票データ保存
        self.vote_data[vote_id] = {
            "question": question,
            "options": opts,
            "votes": {}
        }

        embed = discord.Embed(
            title="📊 投票開始",
            description=question,
            color=discord.Color.green()
        )
        embed.add_field(name="選択肢", value="\n".join(opts), inline=False)

        view = VoteView(opts, vote_id, self.bot, self.vote_data)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="vote_result", description="投票の結果を表示する")
    @app_commands.describe(vote_number="投票ID番号（例: 1）")
    async def vote_result(self, interaction: discord.Interaction, vote_number: int):
        vote_id = f"vote_{vote_number}"
        if vote_id not in self.vote_data:
            await interaction.response.send_message("指定された投票IDは存在しません。", ephemeral=True)
            return
        
        data = self.vote_data[vote_id]
        counts = {opt: 0 for opt in data["options"]}
        for vote in data["votes"].values():
            if vote in counts:
                counts[vote] += 1

        result_lines = [f"**{opt}**: {count}票" for opt, count in counts.items()]
        embed = discord.Embed(
            title="📢 投票結果",
            description=data["question"],
            color=discord.Color.blurple()
        )
        embed.add_field(name="集計", value="\n".join(result_lines), inline=False)
        embed.set_footer(text=f"投票数: {len(data['votes'])}")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ButtonVote(bot))
