#record_task機能
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(path)
from dataset.db import add_task
import discord

from datetime import datetime

#Record_taskクラスの定義
class RecordTask:
    def __init__(self, client):
        self.client = client
    #record_task機能
    async def record_task(self, message):
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel
        
        user_id = message.author.id  # ユーザーIDの入力部分を削除し、代わりにメッセージの送信者のIDを取得
        #インプット機能
        async def request_input(embed_message):
            await message.channel.send(embed=embed_message)
            response_msg = await self.client.wait_for('message', check=check)
            return response_msg.content
        #validate機能
        async def validate_input(input_str, validation_func, error_message):
            while not validation_func(input_str):
                embed_error = discord.Embed(title=error_message, description="", color=0xff0000)
                await message.channel.send(embed=embed_error)
                input_str = await request_input(embed_message)
            return input_str
        #整数型確認機能
        def is_int(string):
            try:
                int(string)
                return True
            except ValueError:
                return False
        #datatime確認機能
        def is_valid_datetime(string):
            try:
                datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
                return True
            except ValueError:
                return False
        #高と低しか受け付けない関数
        def is_valid_word(input_str):
            return input_str == "高" or input_str == "低"

    
        embed_time = discord.Embed(title="タスク開始日時を【YYYY-MM-DD HH:MM:SS】形式で入力してね", description="", color=0x00ff00)
        datetime_str = await request_input(embed_time)
        datetime_str = await validate_input(datetime_str, is_valid_datetime, "日時の形式が不正だよ。【YYYY-MM-DD HH:MM:SS】形式で再度入力してね。")

        embed_task = discord.Embed(title="タスクを入力してね", description="", color=0x00ff00)
        task = await request_input(embed_task)

        embed_priority = discord.Embed(title="タスクの優先度を【高】か【低】のどちらかで入力してね",description="", color=0x00ff00)
        priority = await request_input(embed_priority)
        priority =await(validate_input(priority, is_valid_word, "優先度の形式が不正だよ。【高】,【低】のどちらかを再度入力してね。"))

        user_id = message.author.id
        #デフォルトのフラグを未了に設定
        status = "未了"

        add_task(user_id, datetime_str, task, status,priority)

        embed_record = discord.Embed(title="タスクが記録されたよ", description="", color=0x00ff00)
        await message.channel.send(embed=embed_record)
