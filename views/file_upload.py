import tempfile
import streamlit as st
from minio.error import S3Error
import time
import os

def create_page(api):
    st.title("Upload PDF Files")
    col1, col2 = st.columns([0.5,0.5])
    with col2:
        st.markdown("""
                ### Important Notes for RAG Application:
                - Ensure your PDF is clear, legible, and of high quality.
                - The PDF should contain primarily text content for optimal processing.
                - Avoid PDFs with complex layouts, excessive images, or scanned documents.
                - Ideal PDFs are digital-native documents with selectable text.
                - The content should be relevant and accurate for the intended RAG application.
                    
                High-quality, text-rich PDFs will significantly improve the performance and accuracy of the RAG system.
                """)
    with col1:
        st.markdown("""
                ### Instructions and Requirements:
                1. Click on 'Browse files' to select a PDF file from your computer.
                2. Enter a detailed description for the PDF in the text area.
                3. Click the 'Upload PDF' button to upload your file.
                
                """)
        # File uploader
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        # Description input
        pdf_description = st.text_area("Enter PDF description", height=100)

        # Upload button
        if st.button("Upload PDF"):
            if uploaded_file is not None:
                if pdf_description.strip() != "":
                    try:
                        upload_pdf(api, uploaded_file, pdf_description)
                        st.success(f"Successfully uploaded {uploaded_file.name}")
                        st.session_state["file_uploaded"] = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred while uploading: {str(e)}")
                else:
                    st.error("Please enter a description for the PDF.")
            else:
                st.error("Please select a PDF file to upload.")        
    return True

def upload_pdf(api, uploaded_file, pdf_description):
    if uploaded_file:
        try:
            # Create a temporary file to store the uploaded PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Extract file information
            file_name = uploaded_file.name
            file_size = uploaded_file.size  # Size in bytes

            # verify if file with same name exists
            file_exists = False
            for pdf in st.session_state["pdfs"]:
                 if file_name == pdf["file_name"] : 
                     file_exists = True 
                     break
                     
            if not file_exists:
                # Get the current user's ID
                user_id = st.session_state["userdata"]["id"]

                # Define the path to store the file
                # This should be a path to a server or wherever we're storing the PDFs
                object_name = api.upload_pdf_to_minio(tmp_file_path, file_name, file_size)

                # Upload the PDF using the API
                response = api.upload_pdf_with_description(
                    user_id, 
                    file_name, 
                    object_name, 
                    pdf_description, 
                    file_size
                )

                if ("upload_response" in response) and ("metadata_response" in response) and (response["upload_response"]["message"] == "PDF uploaded successfully!") and (response["metadata_response"]["message"] == "PDF metadata added successfully!"):
                    st.success(f"Uploaded {file_name} successfully!")
                    time.sleep(1)
                else:
                    st.error("Failed to upload the PDF. Please try again.")
            else : 
                st.error("Failed to upload the PDF. Please try again with different file name.")     
                time.sleep(1.7)   
        except S3Error as e:
            st.error(f"Failed to upload {file_name} to MinIO: {e}")

        except Exception as e:
            st.error(f"An error occurred while uploading the PDF: {str(e)}")
        finally:
            # Ensure the temporary file is removed
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                
    else:
        st.error("No file uploaded")