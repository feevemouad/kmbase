# import json
# import streamlit as st
# import requests
# from Utils.conversation_memory import ConversationMemory

# def create_page(api):
#     st.button('Clear Chat History', on_click=clear_chat_history)
#     # Store LLM generated responses
#     if "messages" not in st.session_state.keys():
#         st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

#     # Display or clear chat messages
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.write(message["content"])

#     # User-provided prompt
#     if prompt := st.chat_input(disabled=False ):
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.write(prompt)

#     # Generate a new response if last message is not from assistant
#     if st.session_state.messages[-1]["role"] != "assistant":
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking..."):
#                 response = generate_response(prompt)
#                 placeholder = st.empty()
#                 full_response = ''
#                 for item in response:
#                     full_response += item
#                     placeholder.markdown(full_response)
#                 placeholder.markdown(full_response)
#         message = {"role": "assistant", "content": full_response}
#         st.session_state.messages.append(message)

#     return True

# def clear_chat_history():
#     st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# def generate_response(prompt_input:str):
#     string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'. \n"
            
#     payload = {"user_input": string_dialogue + prompt_input}
#     # Convert the payload to JSON
#     json_payload = json.dumps(payload)
    
#     # Set the headers
#     headers = {
#         "Content-Type": "application/json"
#     }
    
#     # Make the POST request
#     response = requests.post("http://127.0.0.1:8000/chat", data=json_payload, headers=headers)
#     st.write(response)
#     output = response.json()
#     return output["response"]


import json
import streamlit as st
import requests
from Utils.conversation_memory import ConversationMemory

def create_page(api):
    st.button('Clear Chat History', on_click=clear_chat_history)
    
    # Initialize conversation memory
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationMemory()
    
    # Initialize messages if not present
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input(disabled=False):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = generate_response(prompt)
                    st.session_state.memory.add_exchange(prompt, response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.markdown(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    return True

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.session_state.memory.clear()

def generate_response(prompt_input):
    system_prompt = f"You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant' giving source if possible. \n"
    context = st.session_state.memory.get_context() if st.session_state.memory.get_context() else "\nno context it is user's first input"
    payload = {
        "system_prompt": system_prompt,
        "user_input": prompt_input,
        "context": context
               }
    headers = {"Content-Type": "application/json"}
    print(payload)
    
    try:
        response = requests.post("http://127.0.0.1:8000/chat", json=payload, headers=headers)
        response.raise_for_status()
        output = response.json()
        return output["response"]
    except requests.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")

if __name__ == "__main__":
    create_page(None)   