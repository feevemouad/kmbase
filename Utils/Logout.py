import streamlit as st

class Logout:
    def __init__(self):
        if st.button("Logout"):
            st.session_state.pop('token', None)
            st.rerun()