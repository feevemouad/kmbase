import streamlit as st
import pandas as pd
import time
from Utils.Logout import Logout

def create_page(api):
    st.title("Account Settings")
    _, col, _ = st.columns([0.1, 0.8, 0.1])
    # Create a form for user information and modifications
    with col:
        with st.form("user_account_form"):
            st.header("Your Account")

            # Display and allow modification of user information
            new_first_name = st.text_input("First Name", st.session_state["userdata"]['first_name'])
            new_last_name = st.text_input("Last Name", st.session_state["userdata"]['last_name'])
            new_username = st.text_input("Username", st.session_state["userdata"]['username'])
            new_email = st.text_input("Email", st.session_state["userdata"]['email'])
            new_password = st.text_input("Password", type="password")


            # Create two columns for Update and Delete buttons
            col1, col2,     _, col3, col4 = st.columns([0.2,0.225,0.15,0.225,0.2])
            
            with col2:
                update_button = st.form_submit_button("Update Account", type = "primary")
            
            with col3:
                delete_button = st.form_submit_button("Delete Account")

        # Handle form submission
        if update_button:
            if new_password != "":
                update_data = {
                    "first_name": new_first_name,
                    "last_name": new_last_name,
                    "username": new_username,
                    "email": new_email,
                    "password": new_password
                }
            else :  
                update_data = {
                    "first_name": new_first_name,
                    "last_name": new_last_name,
                    "username": new_username,
                    "email": new_email
                }

            
            response = api.update_user(st.session_state["userdata"]["id"], update_data)
            
            if response.get("message") == "User updated successfully!":
                st.success("User updated successfully!")
                update_session_state_userdata( new_first_name, new_last_name, new_username, new_email )
                time.sleep(0.7)
                st.rerun()
            else:
                st.error("Error updating user.")

        if delete_button:
            response = api.delete_user(st.session_state["userdata"]["id"])
            st.success(response["message"])
            time.sleep(0.7)
            Logout(show_button=False)

def update_session_state_userdata(  new_first_name, new_last_name, new_username, new_email ):
    st.session_state["userdata"]["username"] = new_username
    st.session_state["userdata"]["email"] = new_email
    st.session_state["userdata"]["first_name"] = new_first_name
    st.session_state["userdata"]["last_name"] = new_last_name    
    return True
