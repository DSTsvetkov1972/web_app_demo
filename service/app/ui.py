from colorama import Fore 
import asyncio
from ui_fns import init_app, on_login, files_uploader, show_tasks_status, show_user_tasks, show_ready_user_tasks
import global_vars
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
#input('HTTP_PROXY' in os.environ)
#input(os.environ['HTTP_PROXY'])


#params = st.query_params
#if 'current_user' in params:
#    current_user = params['current_user']
init_app()

if "app_restarted" in st.session_state:
    st.session_state.app_restarted=True

if "show_ready" not in st.session_state:
    st.session_state.show_ready = False

current_user_id = 17






if on_login(current_user_id):

    #user_messages = get_user_messages(current_user_id)
    #if user_messages[0]:
    #    show_dialog(user_messages[0])
    
    files_uploader(current_user_id)
    #show_earliest_user_task(current_user_id)
    

    # show_tasks_status()
if st.session_state.show_ready:
    st.button("Очередь задач", on_click=lambda:streamlit_js_eval(js_expressions="parent.window.location.reload()") )
    show_ready_user_tasks(current_user_id)
else:
    col1, col2 = st.columns(2)
    with col1:
        st.button("Перейти к выполненным задачам", on_click=lambda d, k, v: d.update({k:v}), args = [st.session_state, 'show_ready', True], use_container_width=True)
    with col2:
        st.button("Остановить обоаботку текущего задания", use_container_width=True, disabled=True, type="primary")
    async def main():
        await asyncio.gather(show_user_tasks(current_user_id), show_tasks_status())
        #await asyncio.gather(show_tasks_status())
        #await asyncio.gather(show_user_tasks(current_user_id))

    asyncio.run(main())


        