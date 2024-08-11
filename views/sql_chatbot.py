import streamlit as st
import requests


def create_page():
    # Set up Streamlit app
    st.subheader("Database Query Chatbot")    
            # Display usage instructions
    with st.expander(label="How to use this chatbot"):
        st.markdown("""
        ### How to use this chatbot:
        1. Select the type of database you're connecting to.
        2. Enter the database URL in the format `username:password@host:port/database_name`.
        3. Type your question about the database.
        4. Click "Get Answer" to see the result.
        """)
    # Input fields
    with st.expander(label="Database Type and URL Selection", expanded = True ):
        database_type = st.selectbox("Select database type", ["Oracle", "MySQL", "PostgreSQL"])
        database_url = st.text_input("Enter database URL")
    container = st.container(border=True)
    with container : 
        user_question = st.text_input("Enter your question about the database")

        # Button to process the query
        if st.button("Get Answer", type="primary"):
            if not database_url or not user_question:
                st.error("Please fill in all the required fields.")
            else:
                with st.chat_message("assistant"):
                    with st.spinner("Processing your query..."):
                        try:
                            response = requests.post(
                                f"http://localhost:8000/database_query",
                                json={
                                    "database_type": database_type,
                                    "database_url": database_url,
                                    "user_question": user_question
                                }
                            )
                            response.raise_for_status()
                            result = response.json()
                            st.markdown(f"""
        :orange[**Answer :**] {result["answer"]["result"]}""")
                        except requests.exceptions.RequestException as e:
                            st.error(f"An error occurred: {str(e)}")

