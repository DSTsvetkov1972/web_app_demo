import streamlit as st
import os
import asyncio
from colorama import Fore
import threading as th
from time import sleep
from models import processor
from db_fns import (init_db, create_user, put_task_in_queue,
                     get_first_taskid_id_in_queue, get_tasks_ids, get_task_info,
                     reset_processing_to_queued, set_db_column_value, get_all_tasks_ids)
from streamlit_js_eval import streamlit_js_eval
import global_vars


def worker():
    while True:
        taskid_id = get_first_taskid_id_in_queue()
        if taskid_id:
            task = get_task_info(taskid_id)
            print(Fore.YELLOW, f'Добавлена задача:\n{task}', Fore.RESET)
            if task:
                processor(task)
                continue
        # print('ping worker')
        sleep(1)


def init_worker_thread():
    reset_processing_to_queued()
    if 'worker_thread' not in [thread.name for thread in th.enumerate()]:
        global_vars.worker_thread = th.Thread(target=worker,
                                              name='worker_thread')
        global_vars.worker_thread.start()


def complit_task(task_id):
    print(Fore.RED, "Мы здесь!", Fore.RESET)

    task_info = get_task_info(task_id)
    print(Fore.MAGENTA, task_info, Fore.RESET)

    user_folder = os.path.join(os.getcwd(), 'data', str(task_info['user_id']))
    print(Fore.RED, user_folder, Fore.RESET)
    task_input_file = os.path.join(user_folder, 'input', task_info['file_name'])
    task_output_file = os.path.join(user_folder, 'output', f'{task_info["file_name"]}.docx')
    if task_info['task_status'] == 'ready':
        print(Fore.MAGENTA, os.path.exists(task_input_file), Fore.RESET)
        if os.path.exists(task_input_file):
            os.remove(task_input_file)
        if os.path.exists(task_output_file):
            os.remove(task_output_file)

    elif task_info['task_status'] == 'error' and task_info['task_rem'] != 'Already was puted in queue':
        print(Fore.MAGENTA, os.path.exists(task_input_file), Fore.RESET)
        if os.path.exists(task_input_file):
            print(Fore.MAGENTA, task_input_file, Fore.RESET)
            os.remove(task_input_file)

        if os.path.exists(task_output_file):
            print(Fore.MAGENTA, task_output_file, Fore.RESET)
            os.remove(task_output_file)

    set_db_column_value(task_id, 'task_status', "'complited'")


    # streamlit_js_eval(js_expressions="parent.window.location.reload()")


def init_app():
    if not global_vars.app_activated:
        init_db()
        init_worker_thread()
        global_vars.app_activated = True


def on_login(current_user_id):

    current_user_folder = os.path.join(os.getcwd(), 'data', f"{current_user_id}")
    current_user_input_folder = os.path.join(current_user_folder, 'input')
    current_user_output_folder = os.path.join(current_user_folder, 'output')

    print(current_user_folder)
    print(current_user_input_folder)
    print(current_user_output_folder)

    if not os.path.exists(current_user_folder):
        os.makedirs(current_user_folder)
    if not os.path.exists(current_user_input_folder):
        os.makedirs(current_user_input_folder)
    if not os.path.exists(current_user_output_folder):
        os.makedirs(current_user_output_folder)

    create_user(current_user_id)
    with st.sidebar:
        st.write("**Оператор:**")
        st.text_input("Оператор:", current_user_id, disabled=True, label_visibility='collapsed')
        st.button('Выйти из аккаунта', disabled=True, use_container_width=True)

    return True


def files_uploader(user_id):
    with st.sidebar:
        with st.expander('Загрузите файлы для обработки:'):
            uploaded_files = st.file_uploader("Загрузите файлы для обработки",
                                              accept_multiple_files=True,
                                              label_visibility="collapsed")
            if uploaded_files != []:

                for uploaded_file in uploaded_files:
                    file_name = uploaded_file.name
                    file_full_path = os.path.join(os.getcwd(), 'data', f'{user_id}', 'input', file_name)

                    if not os.path.exists(file_full_path):
                        bytes_data = uploaded_file.getvalue()
                        with open(file_full_path, "wb") as file:
                            file.write(bytes_data)
                        put_task_in_queue(user_id, file_name, task_status='queued')
                    else:
                        put_task_in_queue(user_id, file_name, task_status='error')

                streamlit_js_eval(js_expressions="parent.window.location.reload()")


async def show_tasks_status():

    while True:
        with st.sidebar:
            placeholder = st.empty()
            tasks_ids = get_all_tasks_ids()
            with placeholder.container(border=True):
                if tasks_ids:
                    for task_id in tasks_ids[:5]:
                        task_info = get_task_info(task_id[0])
                        # st.write(get_tasks_ids())

                        st.header(f"**Задача: {task_info['user_id']}"
                                  f"-{task_info['task_id']}**")
                        if task_info['task_status'] == 'processing':

                            if task_info['task_progress']:
                                st.progress(int(task_info['task_progress']))
                            st.html(f'<b>В очереди с:</b><br><font color="grey">'
                                    f'{task_info["task_timestamp"][:19]}<br>'
                                    f'<b><font color="black">Обработка стартовала:</b>'
                                    f'<br><font color="grey">{task_info["task_timestamp"][:19]}')

                        else:
                            st.html(f'<b>В очереди с:</b><br><font color="grey">{task_info["task_timestamp"][:19]}')

        await asyncio.sleep(0.5)
        placeholder.empty()


async def show_user_tasks(current_user_id):
    placeholder = st.empty()
    i = 0
    while True:
        i += 1
        placeholder.empty()
        with placeholder.container():
            tasks_ids = get_tasks_ids(current_user_id)
            if tasks_ids:
                for task_id in tasks_ids:
                    task_info = get_task_info(task_id[0])
                    with st.container(border=True):
                        if task_info['task_status'] == 'queued':
                            st.markdown(f'#### :orange[{current_user_id}-{task_id[0]}]')
                            st.markdown(f'### :orange[{task_info["file_name"]} ожидает обработки]')
                            st.markdown(f'Время постановки в очередь: {task_info["task_timestamp"][:19]}')

                        if task_info['task_status'] == 'error':
                            st.markdown(f'#### :red[{current_user_id}-{task_id[0]}]')
                            st.markdown(f'### :red[{task_info["file_name"]} - ошибка обработки]')
                            st.markdown(f':red[{task_info["task_rem"]}]')
                            st.markdown(f'Время постановки в очередь: {task_info["task_timestamp"][:19]}')
                            st.markdown(f'Время начала обработки: {task_info["start_processing_timestamp"][:19]}')
                            st.markdown(f'Время окончания обработки: {task_info["task_progress_timestamp"][:19]}')

                        elif task_info['task_status'] == 'processing':
                            st.markdown(f'#### :blue[{current_user_id}-{task_id[0]}]')
                            st.markdown(f'### :blue[{task_info["file_name"]} обрабатывается]')
                            if task_info['task_progress']:
                                st.progress(int(task_info['task_progress']))
                            st.markdown(f'Время постановки в очередь: {task_info["task_timestamp"][:19]}<br>'
                                    f'Время начала обработки: {task_info["start_processing_timestamp"][:19]}')

                        elif task_info['task_status'] == 'ready':
                            st.markdown(f'#### :green[{current_user_id}-{task_id[0]}]')
                            st.markdown(f'### :green[{task_info["file_name"]} обработан]')
                            st.markdown(f'Время постановки в очередь: {task_info["task_timestamp"][:19]}')
                            st.markdown(f'Время начала обработки: {task_info["start_processing_timestamp"][:19]}')
                            st.markdown(f'Время окончания обработки: {task_info["task_progress_timestamp"][:19]}')

        await asyncio.sleep(2)


def show_ready_user_tasks(current_user_id):
    tasks_ids = get_tasks_ids(current_user_id, "'ready', 'error'")
    if tasks_ids:
        for task_id in tasks_ids:
            if f"{task_id[0]}" in st.session_state:
                if st.session_state[f"{task_id[0]}"]:
                    complit_task(task_id[0])

            task_info = get_task_info(task_id[0])
            if task_info['task_status'] != 'complited':
                with st.container(border=True):

                    if task_info['task_status'] == 'error':
                        st.markdown(f'### :red[{current_user_id}-{task_id[0]} {task_info["file_name"]}]')
                        st.markdown(f':red[{task_info["task_rem"]}]')
                        col1, col2 = st.columns(2)
                        with col1:
                            st.button("❌ Завершить задачу",
                                        key=f'{task_info["task_id"]}',
                                        use_container_width=True)
                        if task_info["task_rem"] != 'Already was puted in queue':
                            with col2:
                                st.button("🐞 Отправить отчет об ошибке", key=f'send_err_{task_info["task_id"]}', use_container_width=True, disabled=True)

                    elif task_info['task_status'] == 'ready':
                        st.markdown(f'### :green[{current_user_id}-{task_id[0]} {task_info["file_name"]}]')
                        col1, col2 = st.columns(2)
                        with col1:
                            st.button("❌ Завершить задачу", key=f'{task_info["task_id"]}', use_container_width=True)

                        with col2:
                            with open(os.path.join(os.getcwd(),
                                                   'data',
                                                    f"{current_user_id}",
                                                    'output',
                                                    f"{task_info['file_name']}.docx"), 'rb') as file_to_download:
                                st.download_button("📥 Загрузить результат",
                                                    file_to_download,
                                                    use_container_width=True,
                                                    key=f'ready_download_{task_info["task_id"]}',
                                                    file_name=f'{task_info["file_name"]}.docx')
