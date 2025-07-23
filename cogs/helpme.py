import discord
from discord.ext import commands
from discord import app_commands

class HelpMe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # 各Cogのコマンド説明リスト（ファイル名: [(コマンド, 説明), ...]）
        self.commands_info = {
            "auth_role.py": [
                ("!setup_auth_message", "リアクションでロール認証メッセージ作成"),
            ],
            "bulk_message_sender.py": [
                ("!bulk_send_message", "複数チャンネルに同じメッセージを一括送信"),
            ],
            "bulk_nickname_setter.py": [
                ("!bulk_set_nick", "複数メンバーのニックネーム一括変更"),
            ],
            "delete_category.py": [
                ("!delete_category", "指定カテゴリと配下チャンネルを削除"),
            ],
            "dice_roller.py": [
                ("!roll", "1d100など汎用ダイスロール"),
            ],
            "generic_button_vote.py": [
                ("/start_vote", "ボタン投票を開始"),
                ("/vote_result", "投票結果を表示"),
            ],
            "phase_controller.py": [
                ("!next_phase", "進行フェーズを進める"),
                ("!current_phase", "現在のフェーズ確認"),
            ],
            "private_text_channels.py": [
                ("!create_private_channels", "VC参加者用のプライベートテキストチャンネル作成"),
            ],
            "progress_bot.py": [
                ("!progress_add", "進捗状況の追加・更新"),
                ("!progress_show", "進捗状況の表示"),
            ],
            "reminder_bot.py": [
                ("!remind", "指定日時にリマインドメッセージ送信"),
            ],
            "scenario_modifier.py": [
                ("!add_to_scenario", "シナリオロールへのメンバー追加"),
                ("!remove_from_scenario", "シナリオロールからメンバー削除"),
                ("!rename_scenario_channel", "シナリオチャンネル名変更"),
            ],
            "scenario_setup.py": [
                ("!setup_scenario", "シナリオ用チャンネル・ロール作成"),
            ],
            "scheduled_message.py": [
                ("!schedule_message", "指定日時にメッセージ送信予約"),
            ],
            "summary_bot.py": [
                ("!summary_create", "プレイ後のまとめを作成"),
            ],
            "vc_move_manager.py": [
                ("!move_to_vc", "複数VCメンバーを指定VCに一括移動"),
            ],
            "voice_channel_manager.py": [
                ("!create_vcs", "複数VCチャンネルを一括作成"),
            ],
        }

    @app_commands.command(name="helpme", description="Botの全機能を一覧表示します")
    async def helpme(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 Botの全機能一覧",
            description="各Cogのコマンドと機能の説明です。",
            color=discord.Color.blue()
        )
        for file, cmds in self.commands_info.items():
            value = "\n".join(f"`{cmd}` : {desc}" for cmd, desc in cmds)
            embed.add_field(name=file, value=value, inline=False)

        embed.set_footer(text="ご利用ありがとうございます！")

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpMe(bot))
