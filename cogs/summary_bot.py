import discord
from discord.ext import commands

class SummaryBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_threads = {}  # guild_id: thread_channel_id

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def start_summary(self, ctx, *, title: str = "プレイ後のまとめ"):
        """まとめ用のスレッドを作成"""
        channel = ctx.channel
        thread = await channel.create_thread(name=title, type=discord.ChannelType.public_thread)
        self.active_threads[ctx.guild.id] = thread.id
        await ctx.send(f"まとめスレッドを作成しました: {thread.mention}")

    @commands.command()
    async def add_comment(self, ctx, *, comment: str):
        """まとめスレッドにコメントを投稿"""
        thread_id = self.active_threads.get(ctx.guild.id)
        if not thread_id:
            await ctx.send("まとめスレッドが作成されていません。管理者に問い合わせてください。")
            return
        thread = ctx.guild.get_thread(thread_id)
        if not thread:
            await ctx.send("まとめスレッドが見つかりません。")
            return
        await thread.send(f"💬 {ctx.author.display_name} さんのコメント:\n{comment}")
        await ctx.message.delete()

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def end_summary(self, ctx):
        """まとめスレッドをクローズ（アーカイブ）"""
        thread_id = self.active_threads.get(ctx.guild.id)
        if not thread_id:
            await ctx.send("まとめスレッドが作成されていません。")
            return
        thread = ctx.guild.get_thread(thread_id)
        if thread:
            await thread.edit(archived=True, locked=True)
            await ctx.send(f"まとめスレッドをクローズしました。")
        else:
            await ctx.send("まとめスレッドが見つかりません。")
        self.active_threads.pop(ctx.guild.id, None)

async def setup(bot):
    await bot.add_cog(SummaryBot(bot))
