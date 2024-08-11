import time
import streamlit as st
from datetime import datetime

def create_page(api):
    st.title("Dashboard")
    
    tab1, tab2= st.tabs([ "Conversations", "Feedbacks"])
    with tab2:
        feedbacks = api.get_all_feedback()
        feedbacks.sort(key=lambda x: datetime.strptime(x['created_at'], "%a, %d %b %Y %H:%M:%S GMT"), reverse=True)

        for feedback in feedbacks:
            display_feedback(api, feedback)
    with tab1:
        conversations = api.get_all_conversations()
        conversations.sort(key=lambda x: datetime.strptime(x['created_at'], "%a, %d %b %Y %H:%M:%S GMT"), reverse=True)
        
        for conv in conversations:
            display_conversation(api,conv) 

def display_conversation(api, conversation):
    created_at = datetime.strptime(conversation['created_at'], "%a, %d %b %Y %H:%M:%S GMT")
    expander_title = f"Conversation ID: {conversation['id']} - {created_at.strftime('%Y-%m-%d %H:%M:%S')} By {conversation['user_id']}"
    with st.expander(expander_title):
        conversation_md = format_conversation(conversation["conversation"])
        st.markdown(conversation_md)
        if st.button("Delete", key=f"delete_conversation_{conversation['id']}", type="primary", use_container_width = False):
            res = api.delete_conversation(conversation['id'])
            if res.get("status", False): 
                st.success("Deleted successfully!!")
                time.sleep(0.8)
                st.rerun()
            else: 
                st.error("Problem occurred, please try again later.")
                time.sleep(0.8)
                st.rerun()
                
def format_conversation(conversation) :
    markdown_content = f"""
---
### :orange[**Conversation :**]

"""
    for message in conversation:
        role = message['role'].capitalize()
        content = message['content'].replace('\n', '\n>\n>')
        markdown_content += f">`{role}:` {content}\n\n"
    markdown_content += "---"
    return markdown_content
           
            
def format_feedback(feedback):
    feedback_description = feedback['feedback_description'].replace('\n', '\n>\n>')
    markdown_content = f"""
### :orange[**Feedback Description :**]

> {feedback_description}

---
### :orange[**Conversation :**]

"""
    for message in feedback['conversation']:
        role = message['role'].capitalize()
        content = message['content'].replace('\n', '\n>\n>')
        markdown_content += f">`{role}:` {content}\n\n"
    markdown_content += "---"
    return markdown_content

def display_feedback(api, feedback):
    created_at = datetime.strptime(feedback['created_at'], "%a, %d %b %Y %H:%M:%S GMT")
    expander_title = f"Feedback ID: {feedback['id']} - {created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    with st.expander(expander_title):
        feedback_md = format_feedback(feedback)
        st.markdown(feedback_md)
        if st.button("Delete", key=f"delete_feedback_{feedback['id']}", type="primary", use_container_width = False):
            res = api.delete_feedback(feedback['id'])
            if res.get("status", False): 
                st.success("Deleted successfully!!")
                time.sleep(0.8)
                st.rerun()
            else: 
                st.error("Problem occurred, please try again later.")
                time.sleep(0.8)
                st.rerun()
                