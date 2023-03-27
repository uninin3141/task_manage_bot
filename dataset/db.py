import mysql.connector
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

sql_pass =os.environ["SQL_PASSWORD"]
railway_host =os.environ["RAILWAY_HOST"]
railway_user =os.environ["RAILWAY_USER"]
railway_database =os.environ["RAILWAY_DATABASE"]

def get_connection():
    connection = mysql.connector.connect(
        host=railway_host,
        user=railway_user,
        password= sql_pass,
        database=railway_database,
    )
    return connection
#データの取得
def get_tasks(user_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM tasks WHERE user_id = %s",
        (user_id,)
    )

    tasks = cursor.fetchall()
    cursor.close()
    connection.close()

    return tasks
#新規のデータの追加
def add_task(user_id, datetime_str, task,status,priority):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute( "INSERT INTO tasks (user_id, datetime, task,status,priority) VALUES (%s, %s, %s,%s,%s)",
        (user_id, datetime_str, task,status,priority)
    )

    connection.commit()

    cursor.close()
    connection.close()
#ステータス変更機能
def update_status(task_id, user_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "UPDATE tasks SET status = %s WHERE id = %s AND user_id = %s",
            (status, task_id, user_id)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

#24時間経過かつ未了のタスクの出力
def get_expired_tasks(current_time):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    expired_time = current_time - timedelta(days=1)
    cursor.execute(
        "SELECT * FROM tasks WHERE datetime <= %s AND status = '未了' ",
        (expired_time,)
    )

    expired_tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return expired_tasks

