import base64
import json
import streamlit as st
from Utils.Login import Login
from Utils.Logout import Logout
from Utils.Sidebar import Sidebar
from API import API 

def main_app(api):
    print(st.session_state["token"]) #TODO
    Sidebar(api)
    if st.button("Fetch Documents"):
        documents = api.get_all_users()
        if documents:
            st.json(documents)
        else:
            st.error("Failed to fetch documents.")

    # Add more functionalities here
    Logout()
    

def main():
    st.set_page_config(page_title="KM base", page_icon=r"im/favicon.ico")
    if 'token' not in st.session_state:
        api = API("http://127.0.0.1:5000/api", None)
        Login(api.login)
    else:
        api = API("http://127.0.0.1:5000/api", st.session_state["token"])
        main_app(api)

if __name__ == "__main__":
    main()
    
