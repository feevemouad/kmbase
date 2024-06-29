import streamlit as st
from typing import Callable
import time


class Login:
    def __init__(self, on_login: Callable[[str, str], bool]):
        _,col2,_ = st.columns([0.25, 0.5, 0.25])
        with col2:
            st.header("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login", type = "primary"):
                if username and password:
                    token = on_login(username, password)
                    if token:
                        st.session_state['token'] = token
                        st.success("Login successful!")
                        st.session_state['username'] = username
                        time.sleep(0.4)  # Give user time to see the success message
                        st.rerun()
                    else:
                        st.error("Login failed. Please try again.")
                else:
                    st.error("Please enter both username and password.")
            