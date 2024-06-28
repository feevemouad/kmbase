import streamlit as st
import pandas as pd
import time

# Create the User Management page
def create_page(api):
    st.title("User Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Register Users", "View Users", "Edit User Details", "Delete Users"])

    with tab1:
        register_users(api)
    with tab2:
        view_users(api)
    with tab3:
        update_user(api)
    with tab4:
        delete_user(api)   
    
    return True

def register_users(api):
    # Register Users
    _,col2,_ = st.columns([0.1, 0.8, 0.1])
    with col2:
        with st.form("register_form", clear_on_submit=False):
            username = st.text_input("Username")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["User", "Admin"])
            submit_button = st.form_submit_button(label="Register")
            
            if submit_button:
                try:
                    response = api.create_user(
                        username,
                        first_name,
                        last_name,
                        password,
                        email,
                        role
                    )
                    if response["message"] == "User created successfully!":
                        st.success("User created successfully!")
                    if response["message"] == "Error creating user, user may already exist":
                        st.error("Error creating user, user may already exist")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

def view_users(api):
    # View Users
    users = api.get_all_users()
    df = pd.DataFrame(users, columns=["id", "first_name", "last_name", "username", "email", "password_hash", "role", "created_at"])
    _,col2,_ = st.columns([0.05, 0.9, 0.05])
    with col2:

        st.dataframe(df, hide_index=True)
    
def update_user(api):
    # Edit User Details
    if 'update_number_input' not in st.session_state:
        st.session_state.update_number_input = 0
    def reset_update_number_input():
        st.session_state.update_number_input = 0

    _,col2,_ = st.columns([0.15, 0.7, 0.15])
    with col2:
        user_id = st.number_input("Enter User ID", min_value=1, step=1, key='update_number_input')
        if user_id != 0:
            try:
                user_data = api.get_user(user_id)
                with st.form("update_form", clear_on_submit=False):
                    first_name = st.text_input("First Name", user_data.get("first_name", ""))
                    last_name = st.text_input("Last Name", user_data.get("last_name", ""))
                    username = st.text_input("Username", user_data.get("username", ""))
                    email = st.text_input("Email", user_data.get("email", ""))
                    password = st.text_input("Password", type="password")
                    role = st.selectbox("Role", ["Admin", "User"], index=["Admin", "User"].index(user_data.get("role", "User")))
                    submit_button = st.form_submit_button(label="Update User")
                    
                    if submit_button:
                        update_data = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "username": username,
                            "email": email,
                            "password": password,
                            "role": role,
                        }
                        
                        response = api.update_user(user_id, update_data)
                        
                        if response.get("message") == "User updated successfully!":
                            st.success("User updated successfully!")
                            time.sleep(0.4)
                            st.rerun()
                        else:
                            st.error("Error updating user.")
            except: 
                st.error("User not found.")
                
def delete_user(api):
    if 'delete_number_input' not in st.session_state:
        st.session_state.delete_number_input = 0
    def reset_delete_number_input():
        st.session_state.delete_number_input = 0
    # Delete Users
    _,col2,_ = st.columns([0.1, 0.8, 0.1])
    with col2:
        delete_user_id = st.number_input("User ID to delete", min_value=1, step=1, key='delete_number_input')
        if delete_user_id != 0:
            try: 
                user_data = api.get_user(delete_user_id) 
                if user_data.get("status_code") == 404:
                    st.error("User not found.")
                    return
                df = pd.DataFrame([user_data], columns=["id", "first_name", "last_name", "username", "email", "role", "created_at"])
                st.dataframe(df, hide_index=True)

                if st.button("Delete User"):
                    response = api.delete_user(delete_user_id, on_click=reset_delete_number_input)
                    st.success(response["message"])
                    st.rerun()

            except Exception as e:
                st.error(f"Error deleting user.\n {e}")
