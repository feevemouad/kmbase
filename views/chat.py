import time
import streamlit as st
import requests
from Utils.conversation_memory import ConversationMemory

def create_page(api):
    with st.expander("Clear Chat History or Provide Feedback"):
        feedback = st.text_area("Describe your feedback:")
        col1, _, col2 = st.columns([3,1,3])  # Adjust the ratio as needed
        with col1:
            if st.button('Submit Feedback', on_click=send_feedback, args=(api, feedback), use_container_width= True) :
                st.rerun()
        with col2:
            if st.button('Clear Chat History', on_click=clear_chat_history, use_container_width= True, type = "primary") :
                st.rerun()

    # Initialize messages if not present
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationMemory()

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
                    st.sidebar.write(st.session_state.memory.get_context)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    return True

def clear_chat_history():
    st.session_state.memory.clear()
    
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
        "conversation_history": conversation_history
               }
    headers = {"Content-Type": "application/json"}
    print(payload)
    try:
        response = requests.post("http://127.0.0.1:8000/chat", json=payload, headers=headers)
        response.raise_for_status()
        output = response.json()
        return output["answer"], output["source_documents"]

    except requests.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
