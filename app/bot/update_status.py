#update_status機能
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(path)
from dataset.db import update_status
from bot.status_button import StatusButton
import discord

from datetime import datetime

class UpdateStatus:
    def __init__(self, client):
        self.client = client
        self.status_button = StatusButton(client)

    #メインのupdate_status機能
    async def update_status(self, message):
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel
        
        #入力者のidしか受け付けないようにする
        user_id = message.author.id
        
        #インプットされた値をリクエストする関数
        async def request_input(embed_message):
            await message.channel.send(embed=embed_message)
            response_msg = await self.client.wait_for('message', check=check)
            return response_msg.content
        
        #validate関数
        async def validate_input(input_str, validation_func, error_message):
            while not validation_func(input_str):
                embed_error = discord.Embed(title=error_message, description="", color=0xff0000)
                await message.channel.send(embed=embed_error)
                input_str = await request_input(embed_message)
            return input_str
        #整数確認関数
        def is_int(string):
            try:
                int(string)
                return True
            except ValueError:
                return False

        embed_task_id = discord.Embed(title="ステータスを更新したいタスクのIDを数字で入力してね", description="", color=0x00ff00)
        task_id = await request_input(embed_task_id)
        task_id = await validate_input(task_id, is_int, "タスクIDが不正だよ。整数値を再度入力してね。")

        embed_status = discord.Embed(title="新しいタスクのステータスを【未了】、【仕掛中】、【完了】のどれかを入力してね",description="", color=0x00ff00)
        status = await self.status_button.get_status_button(message)

        update_status(task_id, user_id, status)

        embed_update = discord.Embed(title="タスクのステータスが更新されたよ", description="", color=0x00ff00)
        await message.channel.send(embed=embed_update)