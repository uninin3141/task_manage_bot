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


#月日選択クラス
class CalendarEndSelect(Select):
    def __init__(self, year, month, start_day, end_day, **kwargs):
        options = [discord.SelectOption(label=f"{year}年{month}月{i}日", value=f"{year}年{month}月{i}日") for i in range(start_day, end_day + 1)]
        super().__init__(placeholder="予定終了日を選択してね", options=options, min_values=1, max_values=1, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_date = self.values[0]
        await interaction.response.send_message(f"選択された時間: {self.view.selected_date}", ephemeral=True)
        

#時間選択クラス
class TimeEndSelect(Select):
    def __init__(self,start_time, end_time, **kwargs):
        options = [discord.SelectOption(label=f"{i}時", value=f"{i}時") for i in range(start_time, end_time + 1)]
        super().__init__(placeholder="予定終了時間を選択してね", options=options, min_values=1, max_values=1, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_time = self.values[0]
        await interaction.response.send_message(f"選択された時間: {self.view.selected_time}", ephemeral=True)
    

#スタートdatetime選択View
class CalendarEndView(View):
    def __init__(self,message,year,month,last_day,timeout=15):
        super().__init__(timeout=timeout)
        self.selected_date = None
        self.selected_time = None
        self.message = message
        self.year = year
        self.month = month
        self.last_day = last_day
        self.add_item(CalendarEndSelect(self.year, self.month, 1, 15))
        self.add_item(CalendarEndSelect(self.year, self.month, 16, self.last_day))
        self.add_item(TimeEndSelect(0, 23))
    
    async def on_timeout(self) -> None:
        if not self.selected_date or not self.selected_time:
            embed = discord.Embed(title="タイムアウトだよ、もう一度選択してね(15秒以内に入力してね)", description="", color=0xFF0000)
            await self.message.channel.send(embed=embed)
        
        self.stop()


class CalendarEnd:
    def __init__(self,client):
        self.client = client

    async def get_end_date(self,message):

        embed_enddate = discord.Embed(title="予定終了日時をプルタブから15秒以内に選択してね", \
            description="上のタブが1日~15日、真ん中のタブが16日～月末、下のタブが時間だよ。日を上のタブ、真ん中のタブの「どちらか一つ」から、時間を下のタブから一つ選んでね。\
            ただし予定開始日時以前の日時を選ぶとタスク入力ができないよ。", color=0x00ff00)
        await message.channel.send(embed=embed_enddate)

        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        YEAR = now.year
        MONTH = now.month
        last_day = calendar.monthrange(YEAR, MONTH)[1]

        view = CalendarEndView(message,year=YEAR,month=MONTH,last_day=last_day)
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
    
            
   