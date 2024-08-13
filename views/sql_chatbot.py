import time
import streamlit as st
import requests


def create_page(api):
    st.subheader("Database Query Chatbot")    
    
    if "db_llm_model" not in st.session_state : 
        st.session_state["db_llm_model"] = {"provider": "ollama", "model_name": "llama3.1"}       


    # Set up Streamlit app
            # Display usage instructions
    with st.expander(label="How to use this chatbot"):
        st.markdown("""
        ### How to use this chatbot:
        1. Select the type of database you're connecting to.
        2. Enter the database URL in the format `username:password@host:port/database_name`.
        3. Type your question about the database.
        4. Click "Get Answer" to see the result.
        """)
        
    add_model_selection()

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
                                    "user_question": user_question,
                                    "llm_model": st.session_state["db_llm_model"]
                                }
                            )
                            response.raise_for_status()
                            result = response.json()
                            st.markdown(f"""
        :orange[**Answer :**] {result["answer"]["result"]}""")
                            
                            # Store the Q&A in the database
                            conversation = {
                                "question": user_question,
                                "answer": result["answer"]["result"],
                                "database_type": database_type,
                                "database_url": database_url
                            }
                            api.create_sql_database_qa(st.session_state["userdata"]["id"], conversation)

                        except requests.exceptions.RequestException as e:
                            st.error(f"An error occurred: {str(e)}")


def add_model_selection():
    with st.expander("Model Selection", expanded=False):            
        llm_model_choice = st.selectbox(
            "Choose LLM Provider",
            options=["Ollama","OpenAI", "Hugging Face", "Groq", "Together.AI"],
            index=0
        )
            
        if llm_model_choice == "Ollama":
            provider = "ollama" 
            ollama_model_name = st.text_input("Enter Ollama Model Name", value = 'llama3.1')
                
        elif llm_model_choice == "OpenAI":
            provider = "openai"
            openai_model_name = st.text_input("Enter OpenAI Model Name")
            openai_api_key = st.text_input("Enter your API Token", type = "password")
            
        elif llm_model_choice == "Hugging Face":
            provider = "huggingface"
            huggingface_model_name_id = st.text_input("Enter Hugging Face Model/Repo Name ID")
            huggingface_api_token = st.text_input("Enter your API Token", type = "password")
                
        elif llm_model_choice == "Groq":
            provider = "groq"
            groq_api_key = st.text_input("Enter Groq API key", type="password")
                
        elif llm_model_choice == "Together.AI":
            provider = "together"
            together_api_key = st.text_input("Enter Together AI API key", type="password")
            model = st.text_input("Enter model name")

        if st.button("Save Model Choices", type= 'primary'):
            if provider == "ollama":
                st.session_state["db_llm_model"] = {"provider": "ollama", "model_name": ollama_model_name.strip()}
                    
            elif provider == "openai":
                st.session_state["db_llm_model"] = {"provider": "openai", "model_name": openai_model_name.strip(), "api_key": openai_api_key }
                    
            elif provider == "huggingface":
                st.session_state["db_llm_model"] = {"provider": "huggingface","api_key": huggingface_api_token, "model_id": huggingface_model_name_id.strip()}
                    
            elif provider == "groq":
                st.session_state["db_llm_model"] = {"provider": "groq", "api_key": groq_api_key.strip()}
                    
            elif provider == "together":
                st.session_state["db_llm_model"] = {"provider": "together", "api_key": together_api_key.strip(),"model": model.strip()}

            st.success("Model choices saved successfully.")
            time.sleep(0.8)
            st.rerun()
