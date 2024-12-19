# from colorama import Fore
import asyncio
from ui_fns import (init_app, on_login, files_uploader,
                    show_tasks_status, show_user_tasks,
                    show_ready_user_tasks)

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

init_app()

if "app_restarted" in st.session_state:
    st.session_state.app_restarted = True

if "show_ready" not in st.session_state:
    st.session_state.show_ready = False

current_user_id = 1


if on_login(current_user_id):
    files_uploader(current_user_id)

if st.session_state.show_ready:
    col1, col2 = st.columns(2)
    with col1:    
        js_expressions = "parent.window.location.reload()"
        st.button("Перейти в монитор задач",
                  on_click=lambda: streamlit_js_eval(js_expressions=js_expressions),
                  use_container_width=True)
    show_ready_user_tasks(current_user_id)
else:
    col1, col2 = st.columns(2)
    with col1:
        st.button("Перейти к выполненным задачам",
                  on_click=lambda d, k, v: d.update({k: v}),
                  args=[st.session_state, 'show_ready', True],
                  use_container_width=True)
    with col2:
        st.button("Остановить обоаботку текущего задания",
                  use_container_width=True,
                  disabled=True,
                  type="primary")

    async def main():
        await asyncio.gather(show_user_tasks(current_user_id),
                             show_tasks_status())

    asyncio.run(main())
