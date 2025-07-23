import discord
from discord.ext import commands, tasks
import tweepy
import os
import datetime

class TwitterPeriodicPoster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitter_usernames = {}  # {guild_id: {channel_id: username}}
        self.last_tweet_ids = {}     # {guild_id: {username: last_tweet_id}}
        self.check_interval = 300    # 秒間隔（例：5分ごと）
        self.twitter_client = self.init_twitter_client()
        self.twitter_check_task.start()

    def init_twitter_client(self):
        # Twitter APIキーは環境変数などで安全に管理してください
        consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
        consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        return tweepy.API(auth, wait_on_rate_limit=True)

    @commands.command(name="twitter_watch")
    @commands.has_permissions(administrator=True)
    async def twitter_watch(self, ctx, twitter_username: str):
        """
        このサーバーのコマンド実行チャンネルに指定したTwitterユーザーのツイートを定期表示します。
        例: !twitter_watch nasa
        """
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id

        if guild_id not in self.twitter_usernames:
            self.twitter_usernames[guild_id] = {}
        self.twitter_usernames[guild_id][channel_id] = twitter_username.lower()

        if guild_id not in self.last_tweet_ids:
            self.last_tweet_ids[guild_id] = {}

        # 初期化のため最新ツイートIDを取得
        try:
            tweets = self.twitter_client.user_timeline(screen_name=twitter_username, count=1, tweet_mode="extended")
            if tweets:
                self.last_tweet_ids[guild_id][twitter_username.lower()] = tweets[0].id
            else:
                self.last_tweet_ids[guild_id][twitter_username.lower()] = None
        except Exception as e:
            await ctx.send(f"Twitter API取得エラー: {e}")
            return

        await ctx.send(f"Twitterユーザー `{twit
