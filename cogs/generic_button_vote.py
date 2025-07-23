import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from typing import List, Dict

class VoteButton(Button):
    def __init__(self, label: str, vote_id: str, cog):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.vote_id = vote_id
        self.cog = cog
        self.choice = label

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        vote_data = self.cog.vote_data.get(self.vote_id)

        if not vote_data:
            await interaction.response.send_message("この投票は終了または無効です。", ephemeral=True)
            return

        if user_id in vote_data["votes"]:
            await interaction.response.send_message("すでに投票済みです。変更はできません。", ephemeral=True)
            return

        vote_data["votes"][user_id] = self.choice
        await interaction.response.send_message(f"「{self.choice}」に投票しました。", ephemeral=True)

class VoteView(View):
    def __init__(self, options: List[str], vote_id: str, cog, timeout: int = 600):
        super().__init__(timeout=timeout)
        for option in options:
            self.add_item(VoteButton(option, vote_id, cog))

class GenericButtonVote(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # vote_id -> {"question": str, "options": [str], "votes": {user_id: choice}}
        self.vote_data: Dict[str, dict] = {}
        self.vote_counter = 0

    @app_commands.command(name="start_vote", description="ボタン投票を開始します")
    @app_commands.describe(
        question="投票の質問",
        options="カンマ区切りで選択肢を入力（2つ以上）"
    )
    async def start_vote(self, interaction: discord.Interaction, question: str, options: str):
        opts = [opt.strip() for opt in options.split(",") if opt.strip()]
        if len(opts) < 2:
            await interaction.response.send_message("選択肢は2つ以上必要です。", ephemeral=True)
            return

        self.vote_counter += 1
        vote_id = f"vote_{self.vote_counter}"

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
        embed.add_field(name="選択肢", value="\n".join(f"- {o}" for o in opts), inline=False)
        embed.set_footer(text=f"投票ID: {self.vote_counter}")

        view = VoteView(opts, vote_id, self)

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="vote_result", description="投票結果を表示します")
    @app_commands.describe(vote_id="投票ID番号（例: 1）")
    async def vote_result(self, interaction: discord.Interaction, vote_id: int):
        vid = f"vote_{vote_id}"
        if vid not in self.vote_data:
            await interaction.response.send_message("指定された投票IDは存在しません。", ephemeral=True)
            return

        data = self.vote_data[vid]
        counts = {opt: 0 for opt in data["options"]}
        for choice in data["votes"].values():
            if choice in counts:
                counts[choice] += 1

        sorted_results = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        total_votes = len(data["votes"])

        result_text = "\n".join(f"**{opt}**: {count}票" for opt, count in sorted_results)
        embed = discord.Embed(
            title=f"📢 投票結果 - {data['question']}",
            description=result_text,
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"総投票数: {total_votes}")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GenericButtonVote(bot))
