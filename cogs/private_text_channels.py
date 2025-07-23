import discord
from discord.ext import commands
import asyncio

class PrivateTextChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="create_private_texts")
    @commands.has_permissions(manage_channels=True)
    async def create_private_texts(self, ctx, voice_channel: discord.VoiceChannel = None):
        """
        指定VCに参加中のメンバー全員に対して
        それぞれプライベートテキストチャンネルを作成し、本人だけアクセス可能にします。
        コマンド実行者も必ず含みます。

        例:
          !create_private_texts [ボイスチャンネル名またはID]
        voice_channelを指定しない場合は、コマンド実行者がいるVCを対象とします。
        """

        # 対象VCの取得
        if voice_channel is None:
            # 実行者が入っているVCを探す
            if ctx.author.voice and ctx.author.voice.channel:
                voice_channel = ctx.author.voice.channel
            else:
                await ctx.send("対象のVCを指定するか、あなたがVCに参加している必要があります。")
                return

        guild = ctx.guild
        overwrites_base = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.me: discord.PermissionOverwrite(read_messages=True)
        }

        # VC参加者セットを作成しコマンド実行者も必ず追加
        members = set(voice_channel.members)
        members.add(ctx.author)

        created_channels = []

        for member in members:
            # チャンネル名は member名でユニークに
            safe_name = f"pt-{member.name}".lower()

            # 同名チャンネルがある場合は連番付与
            existing = discord.utils.get(guild.text_channels, name=safe_name)
            if existing:
                # 連番探索
                for i in range(2, 100):
                    candidate = f"{safe_name}-{i}"
                    if not discord.utils.get(guild.text_channels, name=candidate):
                        safe_name = candidate
                        break

            overwrites = overwrites_base.copy()
            overwrites[member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            # チャンネル作成
            channel = await guild.create_text_channel(
                name=safe_name,
                overwrites=overwrites,
                reason=f"プライベートテキストチャンネル作成 for {member.name}"
            )
            created_channels.append(channel)

        await ctx.send(f"{len(created_channels)}件のプライベートテキストチャンネルを作成しました。")

async def setup(bot):
    await bot.add_cog(PrivateTextChannels(bot))
