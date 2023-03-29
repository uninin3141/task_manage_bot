import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(path)

import discord
from discord.ui import View, Select
import calendar
import datetime
import pytz
import asyncio

intents = discord.Intents.default()
client = discord.Client(intents=intents)
intents.message_content = True
intents.members = True 

now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
YEAR = now.year
MONTH = now.month
last_day_of_month = calendar.monthrange(YEAR, MONTH)[1]

#月日選択クラス
class CalendarStartSelect(Select):
    def __init__(self, year, month, start_day, end_day, **kwargs):
        options = [discord.SelectOption(label=f"{year}年{month}月{i}日", value=f"{year}年{month}月{i}日") for i in range(start_day, end_day + 1)]
        super().__init__(placeholder="予定開始日を選択してね", options=options, min_values=1, max_values=1, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_date = self.values[0]
        await interaction.response.send_message(f"選択された時間: {self.view.selected_date}", ephemeral=True)

#時間選択クラス
class TimeStartSelect(Select):
    def __init__(self,start_time, end_time, **kwargs):
        options = [discord.SelectOption(label=f"{i}時", value=f"{i}時") for i in range(start_time, end_time + 1)]
        super().__init__(placeholder="予定開始時間を選択してね", options=options, min_values=1, max_values=1, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_time = self.values[0]
        await interaction.response.send_message(f"選択された時間: {self.view.selected_time}", ephemeral=True)

#スタートdatetime選択View
class CalendarStartView(View):
    def __init__(self,message, timeout=10):
        super().__init__(timeout=timeout)
        self.selected_date = None
        self.selected_time = None
        self.message = message
        self.add_item(CalendarStartSelect(YEAR, MONTH, 1, 15))
        self.add_item(CalendarStartSelect(YEAR, MONTH, 16, last_day_of_month))
        self.add_item(TimeStartSelect(0, 23))
    
    async def on_timeout(self) -> None:
        
        if not self.selected_date or not self.selected_time:
            embed = discord.Embed(title="タイムアウトだよ、もう一度選択してね(10秒以内に入力してね)", description="", color=0xFF0000)
            await self.message.channel.send(embed=embed)
        
        self.stop()

class CalendarStart:
    def __init__(self,client):
        self.client = client

    async def get_start_date(self,message):

        embed_startdate = discord.Embed(title="予定開始日時をプルタブから選択してね(上のタブが1日~15日、真ん中のタブが16日～月末、下のタブが時間だよ) ", description="", color=0x00ff00)
        await message.channel.send(embed=embed_startdate)

        view = CalendarStartView(message)
        cal_1 = calendar.TextCalendar().formatmonth(YEAR, MONTH)
        sent_message = await message.channel.send(f"\n```\n{cal_1}```")
        view.message = sent_message
        await message.channel.send(view=view)

         # Viewが完了するまで待機
        await asyncio.sleep(view.timeout)
        if (view.selected_date is not None)and (view.selected_time is not None):
            return view.selected_date + view.selected_time

        else:
            return None
    