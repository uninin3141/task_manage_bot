#record_task機能
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(path)

import discord
import asyncio
import pytz
from datetime import datetime,time,timedelta


from dataset.db import add_task
from bot.calendar_start import CalendarStart,CalendarStartSelect,CalendarStartView
from bot.calendar_end import CalendarEnd
from bot.status_button import StatusButton
from bot.priority_button import PriorityButton

jst = pytz.timezone('Asia/Tokyo')

now = datetime.now(jst)
# 昨日の日付と時刻を計算する
yesterday = now - timedelta(days=1)

#Record_taskクラスの定義
class RecordTask:
    def __init__(self, client):
        self.client = client
        self.calendar_start = CalendarStart(client)
        self.calendar_end = CalendarEnd(client)
        self.priority_button = PriorityButton(client)
        self.status_button = StatusButton(client)
        self.startdatetime_str =None
        self.enddatetime_str = None
        self.priority = None
        self.status =None

    def check(self,message):
        def inner_check(msg):
            return msg.author == message.author and msg.channel == message.channel
        return inner_check
        

    async def record_start_date(self,message):
        self.user_id = message.author.id

        startdatetime_str = await self.calendar_start.get_start_date(message)
        startdatetime_str = startdatetime_str.replace('年', '-').replace('月', '-').replace('日', ' ').replace('時', ':') + '00:00'
        self.startdatetime_str = jst.localize(datetime.strptime(startdatetime_str, "%Y-%m-%d %H:%M:%S"))

    async def record_end_date(self,message):
        self.user_id = message.author.id

        enddatetime_str = await self.calendar_end.get_end_date(message)
        enddatetime_str = enddatetime_str.replace('年', '-').replace('月', '-').replace('日', ' ').replace('時', ':') + '00:00'
        self.enddatetime_str = jst.localize(datetime.strptime(enddatetime_str, "%Y-%m-%d %H:%M:%S"))
    
    async def record_priority(self,message):
        self.user_id = message.author.id
        self.priority =await self.priority_button.get_priority_button(message)
    
#recotd_status機能
    async def record_status(self,message):
        self.user_id = message.author.id

        self.status =await self.status_button.get_status_button(message)

    #record_task機能
    async def record_task(self, message):
        self.user_id = message.author.id
        
        #インプット機能
        async def request_input(embed_message):
            await message.channel.send(embed=embed_message)
            response_msg = await self.client.wait_for('message', check=self.check(message))
            return response_msg.content
        #validate機能
        async def validate_input(input_str, validation_func, error_message):
            while not validation_func(input_str):
                embed_error = discord.Embed(title=error_message, description="", color=0xff0000)
                await message.channel.send(embed=embed_error)
                input_str = await request_input(embed_message)
            return input_str      

        if (self.startdatetime_str <= self.enddatetime_str) and (yesterday <=self.startdatetime_str):

            embed_task = discord.Embed(title="タスクを入力してね", description="", color=0x00ff00)
            task = await request_input(embed_task)

            add_task(self.user_id, self.startdatetime_str, task, self.status,self.priority,self.enddatetime_str)

            embed_record = discord.Embed(title="タスクが記録されたよ", description="", color=0x00ff00)
            await message.channel.send(embed=embed_record)
        else:
            embed = discord.Embed(title="開始日付に昨日以前の日付の入力したり、終了日付が開始日付より前だとエラーになるよ,もう一度初めから入力してね", description="", color=0xff0000)
            await message.channel.send(embed=embed)