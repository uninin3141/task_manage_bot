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

    async def task_announce(self,channel_id):
        while not self.client.is_closed():
            await self.client.wait_until_ready()

            now = datetime.now(pytz.timezone('Asia/Tokyo'))
            expired_tasks = get_expired_tasks(now)
   
            channel = self.client.get_channel(channel_id)

            if expired_tasks:
                embed = discord.Embed(title="24時間経過したタスクだよ\n終わってないとかマ？", color=0xFF0000)

                mentioned_users = []  # メンションされたユーザーを保存するリストを追加

                for task in expired_tasks:
                    user_id = task['user_id']
                    task_time = task['datetime']
                    task_name = task['task']
                    user = await self.client.fetch_user(user_id)

                    if user:
                        embed.add_field(name=f"{user.mention}", value=f"【予定開始日時】{task_time}\n 【タスク名】{task_name}", inline=False)
                        mentioned_users.append(user.mention)  # メンションされたユーザーをリストに追加

                    else:
                        embed.add_field(name="Unknown User", value=f"【予定開始日時】{task_time}\n 【タスク名】{task_name}", inline=False)

                mentioned_users_text = ' '.join(mentioned_users)  # メンションされたユーザーをスペースで区切る
                await channel.send(content=mentioned_users_text)  # メンションされたユーザーを送信
                await channel.send(embed=embed)

            else:
                embed = discord.Embed(title=f"24時間経過したタスクは誰もないよ、気持ち良すぎだろ！", description="", color=0xFF0000)
                await channel.send(embed=embed)                
            
            # 次の通知までの待機時間を計算
            next_check_time = now + timedelta(minutes=720)
            time_to_next_check = (next_check_time - now).total_seconds()
            await asyncio.sleep(time_to_next_check)
