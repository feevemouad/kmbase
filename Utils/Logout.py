import streamlit as st

class Logout:
    def __init__(self, show_button=True):
        if  show_button:
            if st.button("**Logout**", type = "primary"):
                self.clear_session_state()
        else:
            self.clear_session_state()
            
    def clear_session_state(self):
        keys = list(st.session_state.keys())
        for key in keys:
            st.session_state.pop(key)
        st.rerun()
