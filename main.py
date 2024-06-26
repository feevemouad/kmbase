import streamlit as st
import streamlit_authenticator as stauth
from streamlit_option_menu import option_menu
from views import home, my_docs, acc_settings 
import json
import requests
import yaml
from yaml.loader import SafeLoader

def sidebar(authenticator): 
    navigation = ["Home", "My Documents", "Account Settings"]
    with st.sidebar:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
        st.header("Navigation")
        selected = option_menu(
            menu_title = None,
            options = navigation
        )
    if selected == "Home":
        home.create_page()
    if selected == "My Documents":
        my_docs.create_page()

    if selected == "Account Settings":
        acc_settings.create_page(authenticator)
        
        
        

if __name__ == '__main__':
    st.set_page_config(page_title="KM base", page_icon=r"im/favicon.ico")
    

    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    users = json.loads(b''.join(requests.get("http://127.0.0.1:5000/api/users")).decode("utf-8"))
    credentials = {"usernames": {}}
    for user in users:
        credentials["usernames"][user["username"]] = {
            "name": f"{user['first_name']} {user['last_name']}",
            "email": user["email"],
            "password": user["password_hash"]
        }


    authenticator = stauth.Authenticate(
        credentials,
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
        )

    authenticator.login()

    if st.session_state["authentication_status"]:
        sidebar(authenticator)
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')



# import streamlit as st
# import streamlit_authenticator as stauth
# import psycopg2
# from psycopg2.extras import RealDictCursor
# import yaml

# # Database connection function
# def get_db_connection():
#     return psycopg2.connect(
#         host="your_host",
#         database="your_database",
#         user="your_username",
#         password="your_password"
#     )

# # Function to get user credentials from database
# def get_user_credentials():
#     conn = get_db_connection()
#     with conn.cursor(cursor_factory=RealDictCursor) as cur:
#         cur.execute("SELECT username, name, email, password FROM users")
#         users = cur.fetchall()
#     conn.close()

#     credentials = {"usernames": {}}
#     for user in users:
#         credentials["usernames"][user['username']] = {
#             "name": user['name'],
#             "email": user['email'],
#             "password": user['password']
#         }
#     return credentials

# # Function to add a new user to the database
# def add_user_to_db(username, name, email, password):
#     conn = get_db_connection()
#     with conn.cursor() as cur:
#         cur.execute(
#             "INSERT INTO users (username, name, email, password) VALUES (%s, %s, %s, %s)",
#             (username, name, email, password)
#         )
#     conn.commit()
#     conn.close()

# # Load configuration (for cookie settings)
# with open('config.yaml') as file:
#     config = yaml.load(file, Loader=yaml.SafeLoader)

# # Get user credentials from database
# credentials = get_user_credentials()

# # Create an authentication object
# authenticator = stauth.Authenticate(
#     credentials,
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days'],
#     config['preauthorized']
# )

# # Create a login widget
# name, authentication_status, username = authenticator.login('Login', 'main')

# if authentication_status:
#     authenticator.logout('Logout', 'main')
#     st.write(f'Welcome *{name}*')
#     st.title('Some content')
# elif authentication_status == False:
#     st.error('Username/password is incorrect')
# elif authentication_status == None:
#     st.warning('Please enter your username and password')

# # If the user is not authenticated, show a registration widget
# if authentication_status != True:
#     try:
#         if authenticator.register_user('Register user', preauthorization=False):
#             # Add the new user to the database
#             new_user = authenticator.credentials['usernames'][authenticator.username]
#             add_user_to_db(
#                 authenticator.username,
#                 new_user['name'],
#                 new_user['email'],
#                 new_user['password']
#             )
#             st.success('User registered successfully')
#     except Exception as e:
#         st.error(e)