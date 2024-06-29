import streamlit as st
from streamlit_option_menu import option_menu
from Utils.Logout import Logout
import base64

class Sidebar:
    def __init__(self, api):
        self.api = api
        if not "userdata" in st.session_state :
            st.session_state["userdata"] = self.api.get_user_by_username(st.session_state["username"])
        self.navigation = ["Home", "My Documents", "Account Settings"]
        self.nav_icons = ["house", "file-earmark-text", "gear"]
        if st.session_state["userdata"]["role"] == "Admin":
            self.navigation.append("User Management")
            self.nav_icons.append("people")
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
            # Search bar for PDFs
            st.subheader("Search PDFs")
            search_query = st.text_input("Search PDFs")
            # Navigation section using option_menu inside the sidebar
            st.header("Navigation")
            selected = option_menu(
                menu_title=None,
                options=self.navigation,
                icons=self.nav_icons,  # Optional: add icons to the options
                menu_icon="cast",  # Optional: set the menu icon
                default_index=0,  # Optional: set the default selected option
                )            
            with st.expander("Upload File", expanded=False):
                uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
                pdf_description = st.text_area("Description")
                if st.button("Upload"):
                    # Ensure the uploaded_file and pdf_description are passed correctly
                    self.upload_pdf(uploaded_file, pdf_description)

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
                background-color: #c92299;
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
                color: #ffffff;
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

    def upload_pdf(self, uploaded_file, pdf_description):
        if uploaded_file:
            # Process the uploaded PDF file and save it with the description
            # For now, we just print the details
            st.sidebar.success(f"Uploaded {uploaded_file.name} with description: {pdf_description}")
        else:
            st.sidebar.error("No file uploaded")
            
