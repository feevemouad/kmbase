import streamlit as st
from Utils.Login import Login
from Utils.Sidebar import Sidebar
from Views import chat, docs, file_upload, acc_settings, user_management, dashboard
from API import API 



def main_app(api):
    sidebar = Sidebar(api)

    # Use the stored page unless a new selection is made
    selected_page = sidebar.render_sidebar()
    if selected_page == "Home":
        chat.create_page(api)
    elif selected_page == "Documents":
        docs.create_page(api)
    elif selected_page == "Account Settings":
        acc_settings.create_page(api)
    elif selected_page == "User Management":
        user_management.create_page(api)
    elif selected_page == "Upload Files":
        file_upload.create_page(api)
    elif selected_page == "Dashboard":
        dashboard.create_page(api)
    else:
        st.error("Unknown page")

def main():
    st.set_page_config(page_title="KM base", page_icon=r"Images/favicon.ico", layout="wide")
    if 'token' not in st.session_state:
        api = API("http://127.0.0.1:5000/api", None)
        Login(api.login)
    else:
        api = API("http://127.0.0.1:5000/api", st.session_state["token"])
        main_app(api)

if __name__ == "__main__":
    main()
    
