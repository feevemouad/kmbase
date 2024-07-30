from datetime import timedelta
import json
import requests
import yaml
import time
import streamlit as st

class Document():
    def __init__(self, api, config_path):
        self.api = api      
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)["minio"]
        
    def display_documents(self, documents):
        # Display existing PDFs
        st.header("Docs")
        for index, pdf in enumerate(documents):
            with st.expander(f"{index+1}. {pdf['file_name']}"):
                col1, _, col2 = st.columns([0.75,0.1,0.15])
                
                with col1:
                    st.write(f"**Description:** {pdf['description']}")
                    st.write(f"**File Size:** {pdf['file_size']}o")
                    st.write(f"**Uploaded At:** {pdf['uploaded_at']}")
                
                with col2:
                    if st.button("View", key=f"view_{index}", type="primary", use_container_width = True):
                        st.session_state["pdf_path"] = pdf['file_path']
                        st.rerun()

                    if st.button("Edit", key=f"edit_{index}", type="secondary", use_container_width = True):
                        if st.session_state["userdata"]["id"] == pdf["user_id"] or st.session_state["userdata"]["role"] == "Admin":
                            st.session_state.editing = pdf["id"]
                            st.rerun()
                        else : 
                            st.error("Not Allowed")
                    
                    if st.button("Delete",key=f"del_{index}",  type="secondary", use_container_width = True):
                        if st.session_state["userdata"]["id"] == pdf["user_id"] or st.session_state["userdata"]["role"] == "Admin" :    
                            status = self.delete_pdf(pdf['id'], pdf['file_path'])
                            print(status)
                            if status :
                                st.session_state["file_deleted"] = True
                                st.rerun()  
                        else : st.error("Not Allowed")
        
            

    def edit_pdf_form(self, pdf_id):
        st.subheader("Edit PDF Metadata")
        
        # Fetch current PDF data
        current_pdf = self.get_pdf(pdf_id)
        
        # Create form for editing
        with st.form("edit_pdf_form"):
            new_file_name = st.text_input("New File Name", value=current_pdf['file_name'])  
            new_description = st.text_area("New Description", value=current_pdf["description"])
            
            submitted = st.form_submit_button("Save Changes")
            
            if submitted:
                response = self.api.edit_pdf_metadata(pdf_id, new_file_name, new_description)
                if "message" in response and response["message"] == "PDF metadata updated successfully":
                    st.session_state["editing"] = None
                    st.session_state["file_edited"] = True
                    st.success("PDF metadata updated successfully!")
                    time.sleep(1)
                    st.rerun()
                else: 
                    st.error(response)
        if st.button("Cancel"):
            st.session_state["editing"] = None
            st.rerun()


    def get_pdf(self, target_id):
        for item in st.session_state["pdfs"]:
            if item['id'] == target_id:
                return item
        return None

    def delete_pdf(self, index, file_path):
        try : 
            response = self.api.delete_pdf(index)
            if response["message"] == "PDF deleted successfully!" : 
                res = self.api.delete_file_from_minio(file_path)
                if res == True : 
                    st.success("pdf deleted successfully")
                    time.sleep(1)
                    return True
                else: return False
            
            else : 
                st.error(f"Error deleting PDF")
                time.sleep(1)
                return False        
        except Exception as e:
            st.error(f"Error deleting PDF: {e}")
            return False 
        
    def show_pdf(self, object_name):
        if st.button("Close", type="primary") : 
            st.session_state["pdf_path"] = None
            st.rerun() 
        client = self.api.initialize_minio_client()
        url = client.presigned_get_object(self.config["docs_bucket"], object_name, expires=timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=1, weeks=0))  # URL expires in 1 hour
        st.markdown(f'<iframe src="{url}" width="1000" height="800"></iframe>', unsafe_allow_html=True)
        
    def get_all_pdfs(self):
        if "file_uploaded" in st.session_state and st.session_state["file_uploaded"] :
            st.session_state["filtered_documents"] = None
            st.session_state["search_query"] = ""
            st.session_state["file_uploaded"] = False
            st.session_state["pdfs"] = self.api.get_all_pdfs_with_description()
            return st.session_state["pdfs"]
        
        if "file_deleted" in st.session_state and st.session_state["file_deleted"] :
            st.session_state["filtered_documents"] = None
            st.session_state["search_query"] = ""
            st.session_state["file_deleted"] = False
            st.session_state["pdfs"] = self.api.get_all_pdfs_with_description()
            return st.session_state["pdfs"]
        
        if "file_edited" in st.session_state and st.session_state["file_edited"] :
            st.session_state["filtered_documents"] = None
            st.session_state["search_query"] = ""
            st.session_state["file_edited"] = False
            st.session_state["pdfs"] = self.api.get_all_pdfs_with_description()
            return st.session_state["pdfs"]

        if "pdfs" not in st.session_state:
            st.session_state["pdfs"] = self.api.get_all_pdfs_with_description()
        return st.session_state["pdfs"]

    def search_results(self, search_query):
        json_payload = json.dumps({"query": search_query})
        headers = {"Content-Type": "application/json"}
        response = requests.post("http://127.0.0.1:8000/search", data=json_payload, headers=headers)
        output = response.json()
        return output["document_names"]
