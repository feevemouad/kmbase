import time
import streamlit as st
from datetime import datetime

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
                st.error("Problem occued, please try again later.")
                time.sleep(0.8)
                st.rerun()
                

def create_page(api):
    st.title("Feedbacks")

    feedbacks = api.get_all_feedback()
    feedbacks.sort(key=lambda x: datetime.strptime(x['created_at'], "%a, %d %b %Y %H:%M:%S GMT"), reverse=True)

    for feedback in feedbacks:
        display_feedback(api, feedback)