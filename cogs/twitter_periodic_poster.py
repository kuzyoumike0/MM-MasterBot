import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import tweepy
import asyncio

class TwitterPeriodicPoster(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # {guild_id: {channel_id: twitter_username}}
        self.watchlist = {}

        # {guild_id: {twitter_username: last_tweet_id}}
        self.last_tweet_ids = {}

        # Twitter API初期化
        self.twitter_client = self.init_twitter_client()

        # 5分間隔でチェックするタスク開始
        self.check_twitter.start()

    def init_twitter_client(self):
        consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
        consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise ValueError("Twitter APIキーが環境変数に設定されていません。")

        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        return tweepy.API(auth, wait_on_rate_limit=True)

    @app_commands.command(name="twitter_watch", description="このチャンネルにTwitterアカウントのツイートを定期投稿します")
    @app_commands.checks.has_permissions(administrator=True)
    async def twitter_watch(self, interaction: discord.Interaction, username: str):
        guild_id = interaction.guild.id
        channel_id = interaction.channel.id
        username = username.lower()

        # 登録処理
        if guild_id not in self.watchlist:
            self.watchlist[guild_id] = {}
        self.watchlist[guild_id][channel_id] = username

        if guild_id not in self.last_tweet_ids:
            self.last_tweet_ids[guild_id] = {}

        # 最新ツイートIDを取得して初期化
        try:
            tweets = self.twitter_client.user_timeline(screen_name=username, count=1, tweet_mode="extended")
            if tweets:
                self.last_tweet_ids[guild_id][username] = tweets[0].id
            else:
                self.last_tweet_ids[guild_id][username] = None
        except Exception as e:
            await interaction.response.send_message(f"T_
