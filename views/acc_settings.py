import streamlit as st
def create_page(authenticator):
    st.title("Account Settings")
    try:
        if authenticator.reset_password(st.session_state["username"]):
            st.success('Password modified successfully')
    except Exception as e:
        st.error(e)

    return True