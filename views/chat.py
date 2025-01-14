import time
import streamlit as st
import requests
from Utils.conversation_memory import ConversationMemory

def create_page(api):
    # Initialize conversation_id in session state if not present
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
        
    if st.session_state["userdata"]["role"] == "SuperUser":
        add_model_selection()      
        
    if "llm_model" not in st.session_state : 
        st.session_state["llm_model"] = {"provider": "ollama", "model_name": "llama3.1"}       
    
    with st.expander("Clear Chat History or Provide Feedback"):
        feedback = st.text_area("Describe your feedback:")
        col1, _, col2 = st.columns([3,1,3])  # Adjust the ratio as needed
        with col1:
            if st.button('Submit Feedback', on_click=send_feedback, args=(api, feedback), use_container_width= True) :
                st.rerun()
        with col2:
            if st.button('Clear Chat History', use_container_width= True, type = "primary") :
                clear_chat_history(api)
                st.rerun()

    # Initialize messages if not present
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationMemory()
        try :
            res = api.create_conversation(st.session_state["userdata"]["id"], st.session_state.memory.history)
            st.session_state.conversation_id = res["conversation_id"]
        except Exception as e:
            st.error("error saving conversation")
    

    # Display chat messages
    for message in st.session_state.memory.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input(disabled=False):
        st.session_state.memory.add_exchange({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer, source_documents = generate_response(prompt)
                    # if source_documents:
                    #     answer += "\nsources: "
                    #     for doc in source_documents:
                    #         answer += f"\n- {doc}"
                    st.session_state.memory.add_exchange({"role": "assistant", "content": answer})
                    st.markdown(answer)
                    # Update the conversation in the database
                    api.update_conversation(st.session_state.conversation_id, st.session_state.memory.history)

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    return True

def clear_chat_history(api):
    st.session_state.memory.clear()
    try :
        res = api.create_conversation(st.session_state["userdata"]["id"], st.session_state.memory.history)
        st.session_state.conversation_id = res["conversation_id"]
    except Exception as e:
        st.error("error saving conversation")

    
def send_feedback(api, feedback):
    chat_history = st.session_state.memory.history
    try:
        api.create_feedback(st.session_state["userdata"]["id"], chat_history, feedback)
        st.success("Feedback submitted successfully!")
        time.sleep(0.8)
    except Exception as e:
        st.error(f"Failed to send feedback: {str(e)}")
        time.sleep(0.8)

def generate_response(prompt_input):
    conversation_history = st.session_state.memory.get_context()
    payload = {
        "user_input": prompt_input,
        "conversation_history": conversation_history,
        "llm_model": st.session_state["llm_model"]
               }
    print(payload)
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post("http://127.0.0.1:8000/chat", json=payload, headers=headers)
        response.raise_for_status()
        output = response.json()
        return output["answer"], output["source_documents"]

    except requests.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")


def add_model_selection():
    with st.expander("Model Selection"):            
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
            model = st.text_input("Enter model name")
                
        elif llm_model_choice == "Together.AI":
            provider = "together"
            together_api_key = st.text_input("Enter Together AI API key", type="password")
            model = st.text_input("Enter model name")

        if st.button("Save Model Choices", type= 'primary'):
            if provider == "ollama":
                st.session_state["llm_model"] = {"provider": "ollama", "model_name": ollama_model_name.strip()}
                    
            elif provider == "openai":
                st.session_state["llm_model"] = {"provider": "openai", "model_name": openai_model_name.strip(), "api_key": openai_api_key }
                    
            elif provider == "huggingface":
                st.session_state["llm_model"] = {"provider": "huggingface","api_key": huggingface_api_token, "model_id": huggingface_model_name_id.strip()}
                    
            elif provider == "groq":
                st.session_state["llm_model"] = {"provider": "groq", "api_key": groq_api_key.strip(),"model_name": model.strip()}
                    
            elif provider == "together":
                st.session_state["llm_model"] = {"provider": "together", "api_key": together_api_key.strip(),"model": model.strip()}

            st.success("Model choices saved successfully.")
            time.sleep(0.8)
            st.rerun()
