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

class ChoicePriorityButton(Button):
    async def callback(self, interaction: discord.Interaction):
        self.view.selected_label = self.label
        await interaction.response.send_message(f"{interaction.user.display_name} さんが '{self.view.selected_label}' を選びました。", ephemeral=True)


class ChoicePriorityView(View):
    def __init__(self,message,timeout=4):
        super().__init__(timeout=timeout)
        self.selected_label = None
        self.message = message
        self.add_item(ChoicePriorityButton(label="高", custom_id="high"))
        self.add_item(ChoicePriorityButton(label="低", custom_id="low"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return not interaction.user.bot
    
    async def on_timeout(self) -> None:
        if not self.selected_label:
            embed = discord.Embed(title="タイムアウトだよ、もう一度選択してね(10秒以内に入力してね)", description="", color=0xFF0000)
            await self.message.channel.send(embed=embed)
        
        self.stop()


class PriorityButton:
    def __init__(self,client):
        self.client = client

    async def get_priority_button(self,message):

        embed_priority = discord.Embed(title="優先度を選択してね", description="", color=0x00ff00)
        await message.channel.send(embed=embed_priority)

        view = ChoicePriorityView(message)
        await message.channel.send(view=view)

        # Viewが完了するまで待機
        await asyncio.sleep(view.timeout)
        if view.selected_label is not None:
            return view.selected_label
        else:
            return None