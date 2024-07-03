import base64
import json
import streamlit as st
from Utils.Login import Login
from Utils.Sidebar import Sidebar
from Views import home, my_docs, file_upload, acc_settings, user_management
from API import API 

def main_app(api):
    # st.write(st.session_state)
    print("**token:** \n"+st.session_state["token"])
    sidebar = Sidebar(api)
    
    page = sidebar.render_sidebar()
    
    if page == "Home":
        home.create_page(api)
        
    elif page == "My Documents":
        my_docs.create_page(api)
        
    elif page == "Account Settings":
        acc_settings.create_page(api)
        
    elif page == "User Management":
        user_management.create_page(api)
          
    elif page == "Upload Files":
        file_upload.create_page(api)
        
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
    
