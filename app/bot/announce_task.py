import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(path)
import asyncio
import discord
import pytz
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from dataset.db import get_expired_tasks

class AnnounceTask:
    def __init__(self, client):
        self.client = client
      
    #ユーザーネーム取得関数    
    async def get_username(self, user_id):
        user = await self.client.fetch_user(user_id)
        return f"{user.name}#{user.discriminator}"
    
    
    #task_announce関数
    async def task_announce(self,channel_id):
        while not self.client.is_closed():
            await self.client.wait_until_ready()

            now = datetime.now(pytz.timezone('Asia/Tokyo'))
            tasks = get_expired_tasks(now)
   
            channel = self.client.get_channel(channel_id)

            if tasks:
                
                df = pd.DataFrame(tasks, columns=["id","user_id", "status", "priority", "datetime", "task"])
                # カラム名を変更する
                df = df.rename(columns={'id': 'id', "user_id":"user",'status': '進捗','priority':'優先度','datetime':'開始日時','task':'タスク名'})
                            
                df["user"] = await asyncio.gather(*[self.get_username(user_id) for user_id in df["user"]])
            
                # 日本語フォントの設定
                matplotlib.rcParams['font.family'] = 'IPAexGothic'
                matplotlib.rcParams['axes.unicode_minus'] = False

                #セルの高さ調整関数
                def adjust_cell_height(table, font_size):
                    for key, cell in table.get_celld().items():
                        cell.set_height(font_size * 0.001)

                # フォントサイズ
                font_size = 200

                # プロットの作成
                fig, ax = plt.subplots(figsize=(font_size * 0.55, len(tasks) * font_size * 0.08))
                ax.axis('off')
                ax.axis('tight')
                table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

                # 列幅を調整
                table.auto_set_column_width(col=list(range(len(df.columns))))
                table.set_fontsize(font_size)  # フォントサイズを調整

                # セルの高さを調整
                adjust_cell_height(table, font_size)

                # 画像として保存
                buf = io.BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                buf.seek(0)
                
               
                embed = discord.Embed(title="24時間経過かつ進捗が未了のタスクだよ\n終わってないとかマ？", color=0xFF0000)
                file = discord.File(buf, filename='tasks.png')
                embed.set_image(url="attachment://tasks.png")
                await channel.send(file=file, embed=embed)
                
                

            else:
                embed = discord.Embed(title=f"24時間経過かつ未了のタスクは誰もないよ、気持ち良すぎだろ！", description="", color=0xFF0000)
                await channel.send(embed=embed)                
            
            # 次の通知までの待機時間を計算
            next_check_time = now + timedelta(minutes=720)
            time_to_next_check = (next_check_time - now).total_seconds()
            await asyncio.sleep(time_to_next_check)
