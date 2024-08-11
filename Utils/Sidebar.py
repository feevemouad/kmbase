import time
import streamlit as st
from streamlit_option_menu import option_menu
from Utils.Logout import Logout
import base64

class Sidebar:
    def __init__(self, api):
        self.api = api
        if not "userdata" in st.session_state :
            st.session_state["userdata"] = self.api.get_user_by_username(st.session_state["username"])
        if st.session_state["userdata"]["role"] == "SuperUser":
            self.navigation = ["Home", "DB Assistant", "Documents", "Upload Files", "Account Settings", "User Management", "Dashboard"]
            self.nav_icons = ["alexa", "database","file-earmark-text", "file-earmark-arrow-up", "gear", "people", "diagram-3"]
        elif st.session_state["userdata"]["role"] == "Support" :
            self.navigation = ["Home", "Documents", "Upload Files", "Account Settings"]
            self.nav_icons = ["alexa", "file-earmark-text", "file-earmark-arrow-up", "gear"]
        elif st.session_state["userdata"]["role"] == "User" :
            self.navigation = ["Home", "Documents", "Account Settings"]
            self.nav_icons = ["alexa", "file-earmark-text", "gear"]

        self.fix_sidebar_width()

    def fix_sidebar_width(self):
        st.markdown(
            """
            <style>
                section[data-testid="stSidebar"] {
                    width: 350px !important; # Set the width to your desired value
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def render_sidebar(self):
                
        with st.sidebar:
            Logout()
            self.affiche_profile_and_name()
          
            # Navigation section using option_menu inside the sidebar
            st.header("Navigation")
            selected = option_menu(
                menu_title=None,
                options=self.navigation,
                icons=self.nav_icons,  # Optional: add icons to the options
                # menu_icon="cast",  # Optional: set the menu icon
                default_index=2,  # Optional: set the default selected option
                )            
        return selected
    
    def affiche_profile_and_name(self):
        user_data = st.session_state.get("userdata", {})
        last_name = user_data.get("last_name", "")
        first_name = user_data.get("first_name", "")
        
        LOGO_IMAGE = "Images/profile.png"
        
        st.markdown(
            """
            <style>
            .sidebar-container {
                display: flex;
                align-items: center;
                padding: 10px;
                # background-color: #c92299;
                background-color: #ffffff;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .logo-img {
                width: 50px;
                height: 50px;
                margin-right: 10px;
                border-radius: 5px;
            }
            .logo-text {
                font-weight: bold;
                font-size: 24px;
                # color: #ffffff;
                color: #c92299;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            f"""
            <div class="sidebar-container">
                <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
                <p class="logo-text">{last_name} {first_name}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

