import os 
import sys
from pathlib import Path
import asyncio
import discord

#内部モジュール
from bot.record_task import RecordTask
from bot.check_task import CheckTask
from bot.announce_task import AnnounceTask
from bot.update_status import UpdateStatus

#環境変数からTOKEN読み込み
TOKEN = os.environ["TASKSCHEDULE_DISCORD_BOT_TOKEN"]

#intentsの指定
intents = discord.Intents.default()
client = discord.Client(intents=intents)
intents.message_content = True
intents.members = True 

#channel_idの指定
channel_id = 1088916695894208624

#タスクループ型機能実行
@client.event
async def on_ready():
    print(f'{client.user} がオンラインになりました!')
    await AnnounceTask(client).task_announce(channel_id)

#コマンド機能実行
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("/taskrecord"):
        await RecordTask(client).record_task(message)
    elif message.content.startswith("/taskcheck"):
        await CheckTask(client).check_task(message)    
    elif message.content.startswith("/taskserch"):
        await SerchTask(client).serch_task(message)
    elif message.content.startswith("/updatestatus"):
        await CheckTask(client).check_task(message)
        await UpdateStatus(client).update_status(message)

client.run(TOKEN)
