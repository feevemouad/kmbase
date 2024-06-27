import streamlit as st
from typing import Callable
import time


class Login:
    def __init__(self, on_login: Callable[[str, str], bool]):
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username and password:
                token = on_login(username, password)
                if token:
                    st.session_state['token'] = token
                    st.success("Login successful!")
                    st.session_state['username'] = username
                    time.sleep(1)  # Give user time to see the success message
                    st.rerun()
                else:
                    st.error("Login failed. Please try again.")
            else:
                st.error("Please enter both username and password.")
        