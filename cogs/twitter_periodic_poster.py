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

        await ctx.send(f"Twitterユーザー `{twitter_username}` のツイートを監視します。")

    @tasks.loop(seconds=300)  # 5分ごとにチェック
    async def twitter_check_task(self):
        for guild_id, channel_map in self.twitter_usernames.items():
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            for channel_id, username in channel_map.items():
                channel = guild.get_channel(channel_id)
                if not channel:
                    continue

                last_tweet_id = self.last_tweet_ids.get(guild_id, {}).get(username)

                try:
                    # 新しいツイート取得（since_idで前回以降のツイートのみ取得）
                    tweets = self.twitter_client.user_timeline(
                        screen_name=username,
                        since_id=last_tweet_id,
                        tweet_mode="extended",
                        count=5
                    )
                except Exception as e:
                    # APIエラーなどはログ出力のみ
                    print(f"[TwitterPeriodicPoster] Twitter API取得エラー: {e}")
                    continue

                # 新しいツイートがあれば昇順にしてメッセージ送信
                if tweets:
                    tweets = sorted(tweets, key=lambda t: t.id)
                    for tweet in tweets:
                        # URL生成
                        tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
                        # テキスト取得（リツイートや引用など対応）
                        content = tweet.full_text
                        # メンションを避けるためバッククォートで囲む場合もあるがそのまま送信
                        embed = discord.Embed(description=content, timestamp=tweet.created_at)
                        embed.set_author(name=f"@{username} on Twitter", url=f"https://twitter.com/{username}")
                        embed.add_field(name="リンク", value=f"[ツイートを見る]({tweet_url})", inline=False)

                        # アイコン設定（APIから取得できる場合）
                        if hasattr(tweet.user, "profile_image_url_https"):
                            embed.set_thumbnail(url=tweet.user.profile_image_url_https)

                        await channel.send(embed=embed)

                    # 最後に取得したツイートIDを保存
                    self.last_tweet_ids[guild_id][username] = tweets[-1].id

    @twitter_check_task.before_loop
    async def before_twitter_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(TwitterPeriodicPoster(bot))
