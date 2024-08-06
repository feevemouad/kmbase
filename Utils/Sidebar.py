import streamlit as st
from streamlit_option_menu import option_menu
from Utils.Logout import Logout
import base64

class Sidebar:
    def __init__(self, api):
        self.api = api
        if not "userdata" in st.session_state :
            st.session_state["userdata"] = self.api.get_user_by_username(st.session_state["username"])
        # self.navigation = ["Assistant","Home", "My Documents", "Upload Files", "Account Settings"]
        self.navigation = ["Home", "Documents", "Upload Files", "Account Settings"]
        # self.nav_icons = ["alexa","house", "file-earmark-text", "file-earmark-arrow-up", "gear"]
        self.nav_icons = ["alexa", "file-earmark-text", "file-earmark-arrow-up", "gear"]
        if st.session_state["userdata"]["role"] == "Admin":
            self.navigation.append("User Management")
            self.navigation.append("Dashboard")
            self.nav_icons.append("people")
            self.nav_icons.append("diagram-3")
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
                default_index=1,  # Optional: set the default selected option
                )            
            # st.session_state['current_page'] = selected
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

    def get_default_index(self):
        # Map page names to their index in the option menu
        page_indices = {
            "Home": 0,
            "Documents": 1,
            "Upload Files": 2,
            "Account Settings": 3,
            "User Management": 4
        }
        # Get the current page from session state, defaulting to "Home"
        current_page = st.session_state.get('current_page', "Home")
        # Return the index of the current page
        return page_indices.get(current_page, 0)

