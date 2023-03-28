import mysql.connector
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
sql_pass =os.environ["SQL_PASSWORD"]
railway_host =os.environ["MYSQLHOST"]
railway_user =os.environ["MYSQLUSER"]
railway_database =os.environ["MYSQLDATABASE"]
railway_port = int(os.environ["MYSQLPORT"])

def get_connection():
    connection = mysql.connector.connect(
        host = railway_host,
        user= railway_user,
        password= sql_pass,
        database=railway_database,
        port = railway_port,
    )
    return connection
#未完了データの取得
def get_tasks(user_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM tasks WHERE user_id = %s AND status !='完了' ",
        (user_id,)
    )

    tasks = cursor.fetchall()
    cursor.close()
    connection.close()

    return tasks


#全件データの取得
def get_all_tasks(user_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM tasks WHERE user_id = %s ",
        (user_id,)
    )

    tasks = cursor.fetchall()
    cursor.close()
    connection.close()

    return tasks
#新規のデータの追加
def add_task(user_id, starttime_str, task,status,priority,endtime_str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute( "INSERT INTO tasks (user_id, starttime, task,status,priority,endtime) VALUES (%s, %s, %s,%s,%s,%s)",
        (user_id, starttime_str, task,status,priority,endtime_str)
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
        "SELECT * FROM tasks WHERE endtime <= %s AND status != '完了' ",
        (expired_time,)
    )

    expired_tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return expired_tasks

