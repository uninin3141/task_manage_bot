import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(path)

from dataset.db import get_all_tasks

import discord
#Check_All_Taskクラスの定義
class Check_All_Task:
    def __init__(self, client):
        self.client = client
#check_task機能
    async def check_all_task(self, message):
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        user_id = message.author.id
        
        def create_task_embeds(tasks, tasks_per_embed=5):
            task_embeds = []
            num_embeds = (len(tasks) + tasks_per_embed - 1) // tasks_per_embed

            for i in range(num_embeds):
                start_index = i * tasks_per_embed
                end_index = min(start_index + tasks_per_embed, len(tasks))
                current_tasks = tasks[start_index:end_index]

                embed = discord.Embed(title=f"今までのタスク全部だよ ({start_index + 1} - {end_index})", description="", color=0x0000FF)

                for task in current_tasks:
                    task_details = f"ID: {task['id']}\n進捗: {task['status']}\n優先度: {task['priority']}\n予定開始日時: {task['starttime']}\n予定終了日時: {task['endtime']}"
                    embed.add_field(name=task["task"], value=task_details, inline=False)

                task_embeds.append(embed)

            return task_embeds

        tasks = get_all_tasks(user_id)
        
        if tasks:
            task_embeds = create_task_embeds(tasks)
            for embed in task_embeds:
                await message.channel.send(embed=embed)
        else:
            embed = discord.Embed(title="タスクひとつもないよ最高や！", description="", color=0x0000FF)
            await message.channel.send(embed=embed)

       