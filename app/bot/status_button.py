import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(path)

import discord
from discord.ui import View, Button
from discord.interactions import Interaction
import asyncio


intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.members = True 

client = discord.Client(intents=intents)

class ChoiceStatusButton(Button):
    async def callback(self, interaction: discord.Interaction):
        self.view.selected_label = self.label
        await interaction.response.send_message(f"{interaction.user.display_name} さんが '{self.view.selected_label}' を選びました。", ephemeral=True)

class ChoiceStatusView(View):
    def __init__(self,message,timeout=4):
        super().__init__(timeout=timeout)
        self.selected_label = None  # 選択されたラベルを格納するインスタンス変数を追加
        self.message = message
        self.add_item(ChoiceStatusButton(label="完了", custom_id="completed"))
        self.add_item(ChoiceStatusButton(label="仕掛中", custom_id="in_progress"))
        self.add_item(ChoiceStatusButton(label="未了", custom_id="incomplete"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return not interaction.user.bot
    async def on_timeout(self) -> None:
        embed = discord.Embed(title="タイムアウトだよ、5秒以内にもう一度選択してね", description="", color=0xFF0000)
        if not self.selected_label:
            embed = discord.Embed(title="タイムアウトだよ、もう一度選択してね(10秒以内に入力してね)", description="", color=0xFF0000)
            await self.message.channel.send(embed=embed)
        
        self.stop()

class StatusButton:
    def __init__(self,client):
        self.client = client

    async def get_status_button(self,message):

        embed_status = discord.Embed(title="ステータスを選択してね", description="", color=0x00ff00)
        await message.channel.send(embed=embed_status)

        view = ChoiceStatusView(message)
        await message.channel.send(view=view)
        # Viewが完了するまで待機
        await asyncio.sleep(view.timeout)
        if view.selected_label is not None:
            return view.selected_label
        else:
            return None

