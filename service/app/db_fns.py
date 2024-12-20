import sqlite3
import os
from datetime import datetime
# from colorama import Fore


def init_db():
    conn = sqlite3.connect(os.path.join(os.getcwd(), 'service', 'app', 'app.db'))
    with conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS  tasks"
                    "    (task_id INT, "
                    "    user_id INT, "
                    "    file_name TEXT, "
                    "    task_timestamp TEXT, "
                    "    start_processing_timestamp TEXT, "
                    "    task_progress INT, "
                    "    task_progress_timestamp TEXT, "
                    "    task_status TEXT, "
                    "    task_status_timestamp TEXT, "
                    "    task_rem TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS users"
                    "    (user_id INT, "
                    "    user_id_timestamp TEXT, "
                    "    dialog_message TEXT, "
                    "    toast_message TEXT)")


def create_user(current_user_id):
    conn = sqlite3.connect(os.path.join(os.getcwd(), 'service', 'app', 'app.db'))

    with conn:
        cur = conn.cursor()
        sql = (f"SELECT * FROM users WHERE user_id={current_user_id}")
        cur.execute(sql)
        res = cur.fetchone()
       
        if not res: 
            sql = (f"INSERT INTO users "
                f"(user_id) "
                f"VALUES ({current_user_id})")
            cur.execute(sql)


def create_user_messages(user_id, dialog_message, toast_message):
    conn = sqlite3.connect(os.path.join(os.getcwd(), 'service', 'app', 'app.db'))
    with conn:
        cur = conn.cursor()
        dialog_message = str(dialog_message).replace("'", '"')
        toast_message = str(toast_message).replace("'", '"')
        sql = f"UPDATE users SET dialog_message ='{dialog_message}', toast_message ='{toast_message}' WHERE user_id={user_id}"
        cur.execute(sql)


def get_user_messages(current_user_id):
    conn = sqlite3.connect(os.path.join(os.getcwd(), 'service', 'app', 'app.db'))

    with conn:
        cur = conn.cursor()
        sql = (f"SELECT dialog_message, toast_message "
               f"FROM users "
               f"WHERE user_id = {current_user_id}")
        res = cur.execute(sql).fetchall()[0]
    return res


def put_task_in_queue(user_id, file_name, task_status='queued'):
    conn = sqlite3.connect(os.path.join(os.getcwd(), 'service', 'app', 'app.db'))

    with conn:
        cur = conn.cursor()
        sql = "SELECT max(task_id) FROM tasks"
        cur.execute(sql)
        res = cur.fetchall()[0][0]
        if res:
            max_task_id = res
        else:
            max_task_id = 0
        if task_status == 'queued':
            sql = (f"INSERT INTO tasks "
                   f"    (task_id,"
                   f"    user_id,"
                   f"    file_name,"
                   f"    task_timestamp,"
                   f"    task_status,"
                   f"    task_status_timestamp)"
                   f"VALUES "
                   f"    ({max_task_id+1}, {user_id}, '{file_name}', '{datetime.now()}','queued', '{datetime.now()}')")
        else:
            sql = (f"INSERT INTO tasks "
                   f"    (task_id,"
                   f"    user_id,"
                   f"    file_name,"
                   f"    task_timestamp,"
                   f"    start_processing_timestamp,"
                   f"    task_progress_timestamp,"
                   f"    task_status,"
                   f"    task_status_timestamp,"
                   f"    task_rem)"
                   f"VALUES "
                   f"    ({max_task_id+1}, {user_id}, '{file_name}', '{datetime.now()}', '{datetime.now()}', "
                   f"    '{datetime.now()}', 'error', '{datetime.now()}',  'Already was puted in queue')")
        cur.execute(sql)


def get_tasks_ids(user_id, task_statuses=None):
    conn = sqlite3.connect(os.path.join(os.getcwd(), 'service', 'app', 'app.db'))
    with conn:
        cur = conn.cursor()
        if task_statuses:
            sql = f"SELECT task_id FROM tasks WHERE user_id={user_id} AND task_status IN ({task_statuses}) ORDER BY task_id DESC"
        else:
            sql = f"SELECT task_id FROM tasks WHERE user_id={user_id}  ORDER BY task_id DESC"
        cur.execute(sql)
        res = cur.fetchall()
    if res:
        return res
    else:
        return None


def get_all_tasks_ids():
    conn = sqlite3.connect(os.path.join(os.getcwd(), 'service', 'app', 'app.db'))
    with conn:
        cur = conn.cursor()
        sql = "SELECT task_id FROM tasks WHERE task_status IN ('processing', 'queued') ORDER BY task_id"
        cur.execute(sql)
        res = cur.fetchall()
    if res:
        return res
    else:
        return None


def get_first_taskid_id_in_queue():
    conn = sqlite3.connect(os.path.join(os.getcwd(), 'service', 'app', 'app.db'))
    with conn:
        cur = conn.cursor()
        sql = "SELECT task_id FROM tasks WHERE task_status = 'queued' ORDER BY task_timestamp"
        cur.execute(sql)
        res = cur.fetchall()
    if res:
        return res[0][0]
    else:
        return None


def get_task_info(task_id):
    conn = sqlite3.connect(os.path.join(os.getcwd(), 'service', 'app', 'app.db'))
    with conn:
        cur = conn.cursor()
        sql = f"SELECT * FROM tasks WHERE task_id = {task_id}"
        # print(Fore.RED, sql, Fore.RESET)
        cur.execute(sql)
        res = cur.fetchall()

    if res:
        task_info = res[0]
        return {'task_id': task_info[0],
                'user_id': task_info[1],
                'file_name': task_info[2],
                'task_timestamp': task_info[3],
                'start_processing_timestamp': task_info[4],
                'task_progress': task_info[5],
                'task_progress_timestamp': task_info[6],
                'task_status': task_info[7],
                'task_status_timestamp': task_info[8],
                'task_rem': task_info[9]
                }
    else:
        return None


def set_db_column_value(task_id, column, value):
    conn = sqlite3.connect(os.path.join(os.getcwd(), 'service', 'app', 'app.db'))
    with conn:
        cur = conn.cursor()
        sql = f"UPDATE tasks SET {column}={value} WHERE task_id={task_id}"
        cur.execute(sql)


def reset_processing_to_queued():
    conn = sqlite3.connect(os.path.join(os.getcwd(), 'service', 'app', 'app.db'))
    with conn:
        cur = conn.cursor()
        sql = "UPDATE tasks SET task_status='queued' WHERE task_status='processing'"
        cur.execute(sql)


if __name__ == '__main__':
    create_user(222)
