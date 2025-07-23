import discord
from discord.ext import commands
import json
import os

AUTH_CONFIG_PATH = "data/auth_config.json"

def load_auth_config():
    if not os.path.exists(AUTH_CONFIG_PATH):
        return {}
    with open(AUTH_CONFIG_PATH, "r") as f:
        return json.load(f)

def save_auth_config(config):
    os.makedirs(os.path.dirname(AUTH_CONFIG_PATH), exist_ok=True)
    with open(AUTH_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

class AuthRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auth_config = load_auth_config()  # 認証メッセージ設定: {message_id: {emoji: role_id}}

    @commands.command(name="setup_auth_message")
    @commands.has_permissions(administrator=True)
    async def setup_auth_message(self, ctx, *, pairs: str):
        """
        例: !setup_auth_message ✅=1234 🎭=5678 📢=9012
        各絵文字に対してロールIDを割り当てて認証メッセージを送信
        """
        try:
            emoji_role_map = {}
            for pair in pairs.split():
                emoji, role_id = pair.split("=")
                emoji_role_map[emoji] = int(role_id)
        except Exception:
            return await ctx.send("形式が正しくありません。例: `!setup_auth_message ✅=123456789012 🎭=234567890123`")

        embed = discord.Embed(
            title="✅ リアクションでロール認証",
            description="\n".join([f"{emoji} → <@&{rid}>" for emoji, rid in emoji_role_map.items()]),
            color=discord.Color.blue()
        )
        msg = await ctx.send(embed=embed)

        for emoji in emoji_role_map.keys():
            await msg.add_reaction(emoji)

        # 保存
        self.auth_config[str(msg.id)] = emoji_role_map
        save_auth_config(self.auth_config)

        await ctx.send(f"認証メッセージを送信しました。（ID: `{msg.id}`）")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.message_id) not in self.auth_config:
            return

        emoji = str(payload.emoji.name)
        role_id = self.auth_config[str(payload.message_id)].get(emoji)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role = guild.get_role(role_id)
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if str(payload.message_id) not in self.auth_config:
            return

        emoji = str(payload.emoji.name)
        role_id = self.auth_config[str(payload.message_id)].get(emoji)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role = guild.get_role(role_id)
        member = guild.get_member(payload.user_id)
        if role and member:
            await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(AuthRole(bot))
