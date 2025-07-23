import discord
from discord.ext import commands
import json
import os

AUTH_CONFIG_PATH = "data/auth_config.json"

def load_auth_config():
    if not os.path.exists(AUTH_CONFIG_PATH):
        return {}
    with open(AUTH_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_auth_config(config):
    os.makedirs(os.path.dirname(AUTH_CONFIG_PATH), exist_ok=True)
    with open(AUTH_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

class AuthRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auth_config = load_auth_config()  # {message_id: {emoji: role_id, ...}, ...}

    @commands.command(name="setup_auth_message")
    @commands.has_permissions(administrator=True)
    async def setup_auth_message(self, ctx, *, pairs: str):
        """
        リアクション認証メッセージを作成し、絵文字-ロール名対応を登録する。
        例:
          !setup_auth_message ✅=参加者 🎭=演者 📢=スタッフ
        """
        try:
            emoji_role_map = {}
            for pair in pairs.split():
                emoji, role_name = pair.split("=")
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                if role is None:
                    await ctx.send(f"ロール名 `{role_name}` が見つかりません。正確に入力してください。")
                    return
                emoji_role_map[emoji] = role.id
        except Exception:
            await ctx.send("形式が正しくありません。例: `!setup_auth_message ✅=参加者 🎭=演者`")
            return

        embed = discord.Embed(
            title="✅ リアクションでロール認証",
            description="\n".join([f"{emoji} → <@&{rid}>" for emoji, rid in emoji_role_map.items()]),
            color=discord.Color.blue()
        )
        msg = await ctx.send(embed=embed)

        for emoji in emoji_role_map.keys():
            try:
                await msg.add_reaction(emoji)
            except Exception as e:
                await ctx.send(f"リアクションの追加に失敗しました: {emoji} ({e})")

        self.auth_config[str(msg.id)] = {
            "guild_id": ctx.guild.id,
            "channel_id": ctx.channel.id,
            "emoji_role_map": emoji_role_map
        }
        save_auth_config(self.auth_config)

        await ctx.send(f"認証メッセージを送信しました。（ID: `{msg.id}`）")

    @commands.command(name="list_auth_messages")
    @commands.has_permissions(administrator=True)
    async def list_auth_messages(self, ctx):
        """
        現在登録されている認証メッセージ一覧を表示する
        """
        if not self.auth_config:
            await ctx.send("登録されている認証メッセージはありません。")
            return

        embed = discord.Embed(
            title="📝 登録済みリアクション認証メッセージ一覧",
            color=discord.Color.green()
        )

        for msg_id, info in self.auth_config.items():
            guild_id = info.get("guild_id")
            channel_id = info.get("channel_id")
            emoji_role_map = info.get("emoji_role_map", {})
            jump_url = f"https://discord.com/channels/{guild_id}/{channel_id}/{msg_id}"
            desc = "\n".join([f"{emoji} → <@&{role_id}>" for emoji, role_id in emoji_role_map.items()]) or "なし"

            embed.add_field(
                name=f"📌 メッセージID: {msg_id} ([Jump]({jump_url}))",
                value=desc,
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="remove_auth_message")
    @commands.has_permissions(administrator=True)
    async def remove_auth_message(self, ctx, message_id: int):
        """
        指定したメッセージIDの認証設定を削除する
        """
        if str(message_id) not in self.auth_config:
            await ctx.send("指定されたメッセージIDは登録されていません。")
            return

        self.auth_config.pop(str(message_id))
        save_auth_config(self.auth_config)
        await ctx.send(f"認証メッセージID `{message_id}` の設定を削除しました。")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.message_id) not in self.auth_config:
            return

        info = self.auth_config[str(payload.message_id)]
        emoji = str(payload.emoji.name)
        role_id = info["emoji_role_map"].get(emoji)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role = guild.get_role(role_id)
        member = guild.get_member(payload.user_id)
        if role and member:
            try:
                await member.add_roles(role)
            except Exception:
                pass  # 権限不足など無視

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if str(payload.message_id) not in self.auth_config:
            return

        info = self.auth_config[str(payload.message_id)]
        emoji = str(payload.emoji.name)
        role_id = info["emoji_role_map"].get(emoji)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role = guild.get_role(role_id)
        member = guild.get_member(payload.user_id)
        if role and member:
            try:
                await member.remove_roles(role)
            except Exception:
                pass  # 権限不足など無視

async def setup(bot):
    await bot.add_cog(AuthRole(bot))
