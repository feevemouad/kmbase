import streamlit as st

class Logout:
    def __init__(self):
        if st.button("Logout"):
            keys = list(st.session_state.keys())
            for key in keys:
                st.session_state.pop(key)
            st.rerun()
