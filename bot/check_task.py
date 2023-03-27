import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(path)

from dataset.db import get_tasks

import discord
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import io
#CheckTaskクラスの定義
class CheckTask:
    def __init__(self, client):
        self.client = client
#check_task機能
    async def check_task(self, message):
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        user_id = message.author.id
        
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
        

        tasks = get_tasks(user_id)
        
        #pandasとmatplotlibで画像生成
        # tasksからデータフレームを作成
        df = pd.DataFrame(tasks, columns=["id", "status", "priority", "datetime", "task"])
        # カラム名を変更する
        df = df.rename(columns={'id': 'id', 'status': '進捗','priority':'優先度','datetime':'開始日時','task':'タスク名'})
       
        # 日本語フォントの設定
        matplotlib.rcParams['font.family'] = 'MS Gothic'
        matplotlib.rcParams['axes.unicode_minus'] = False

        #セルの高さ調整関数
        def adjust_cell_height(table, font_size):
            for key, cell in table.get_celld().items():
                cell.set_height(font_size * 0.001)

        # フォントサイズ
        font_size = 130

        # プロットの作成
        fig, ax = plt.subplots(figsize=(font_size * 0.5, len(tasks) * font_size * 0.1))
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


        if tasks:
            file = discord.File(buf, filename='tasks.png')
            embed = discord.Embed(title="タスク一覧だよ", description="", color=0x0000FF)
            embed.set_image(url="attachment://tasks.png")
            await message.channel.send(file=file, embed=embed)
                
        else:
            embed = discord.Embed(title="タスクひとつもないよ最高や！", description="", color=0x0000FF)
            await message.channel.send(embed=embed)
        # プロットを閉じる
        plt.close(fig)

