import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(path)
import asyncio
import discord
import pytz
from datetime import datetime, timedelta
from dataset.db import get_expired_tasks

class AnnounceTask:
    def __init__(self, client):
        self.client = client
      
    #ユーザーネーム取得関数    
    async def get_username(self, user_id):
        user = await self.client.fetch_user(user_id)
        return f"{user.name}"
    #ユーザーメンション取得関数    
    async def get_usermention(self, user_id):
        user = await self.client.fetch_user(user_id)
        return f"{user.mention}"
    
    async def create_task_embeds(self,tasks, tasks_per_embed=5):
        task_embeds = []
        num_embeds = (len(tasks) + tasks_per_embed - 1) // tasks_per_embed

        for i in range(num_embeds):
            start_index = i * tasks_per_embed
            end_index = min(start_index + tasks_per_embed, len(tasks))
            current_tasks = tasks[start_index:end_index]

            embed = discord.Embed(title=f"完了してないタスク一覧だよ、はよやれやカスぅ ({start_index + 1} - {end_index})", description="", color=0x0000FF)

            for task in current_tasks:
                user_name = await self.get_username(task['user_id'])
                task_details = f"ID: {task['id']}\n進捗: {task['status']}\n優先度: {task['priority']}\n予定開始日時: {task['starttime']}\n予定終了日時: {task['endtime']}"
                embed.add_field(name=f"【{user_name}】 {task['task']}", value=task_details, inline=False)

            task_embeds.append(embed)

        return task_embeds
    
    #task_announce関数
    async def task_announce(self,channel_id):
        while not self.client.is_closed():
            await self.client.wait_until_ready()

            now = datetime.now(pytz.timezone('Asia/Tokyo'))
            tasks = get_expired_tasks(now)
   
            channel = self.client.get_channel(channel_id)

            if tasks:
                # タスクのユーザーIDを取得し、メンションを作成
                mentions = ', '.join([await self.get_usermention(task['user_id']) for task in tasks])
                 # メンションを含むメッセージを送信
                await channel.send(f"{mentions} 完了していないタスクがあるよ！")

                task_embeds = await self.create_task_embeds(tasks)
                for embed in task_embeds:
                    await channel.send(embed=embed)

            else:
                embed = discord.Embed(title=f"24時間経過かつ未了のタスクは誰もないよ、気持ち良すぎだろ！", description="", color=0xFF0000)
                await channel.send(embed=embed)                
            
            # 次の通知までの待機時間を計算
            next_check_time = now + timedelta(minutes=720)
            time_to_next_check = (next_check_time - now).total_seconds()
            await asyncio.sleep(time_to_next_check)
