import streamlit as st
from Utils.Document import Document

def create_page(api):
    document_handler = Document(api, "config/config.yaml")
    if not("pdf_path" in st.session_state):
        st.session_state["pdf_path"] = None
        
    if not("editing" in st.session_state):
        st.session_state["editing"] = None
        
    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""
    
    if "filtered_documents" not in st.session_state:
        st.session_state["filtered_documents"] = None

    if st.session_state["pdf_path"] is None and st.session_state["editing"] is None:
        # Only show search input on the main document listing page
        search_query = st.text_input("Search documents", st.session_state["search_query"])
        
        documents = document_handler.get_all_pdfs()
        if search_query != st.session_state["search_query"] or st.session_state["filtered_documents"] is None:
            st.session_state["search_query"] = search_query
            if search_query:
                # Perform search
                search_results = document_handler.search_results(search_query)
                
                # Create a dictionary for quick lookup
                doc_dict = {doc['file_name']: doc for doc in documents}
                
                # Filter and order documents based on search results
                filtered_documents = [doc_dict[name] for name in search_results if name in doc_dict]
                
                st.session_state["filtered_documents"] = filtered_documents
            else:
                st.session_state["filtered_documents"] = documents
        
        document_handler.display_documents(st.session_state["filtered_documents"])
        
    elif st.session_state["pdf_path"] != None :
        st.session_state['current_page'] = "Documents"
        document_handler.show_pdf(st.session_state["pdf_path"])
        
    elif st.session_state["editing"] != None :
        st.session_state['current_page'] = "Documents"
        document_handler.edit_pdf_form(st.session_state["editing"])
    return True


