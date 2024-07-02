import streamlit as st
# from streamlit_elements import elements, dashboard, mui, html

def get_all_pdfs():
    # Replace this with actual API call
    # For this example, I'll mock some data
    return [
        {"title": f"Document {i}", "description": f"Description for document {i}"}
        for i in range(1, 13)
    ]

def create_page(api):
    st.title("Home")
    st.info("Working on ...")
    
    documents = get_all_pdfs()
    cols = st.columns(4)

    for i, doc in enumerate(documents):
        with cols[i % 4]:
            st.write(f"### {doc['title']}")
            st.text_area("Description", doc['description'], height=100, key=f"desc_{i}")
            col1, _, col2, col3 = st.columns([0.25, 0.01, 0.25, 0.3])
            with col1:
                st.button("View", key=f"view_{i}")
            with col2:
                st.button("Edit", key=f"edit_{i}")
            with col3:
                st.button("Delete", key=f"delete_{i}")
            st.write("---")
    # with elements("dashboard"):
    #     # Create a layout based on the number of documents
    #     layout = [
    #         dashboard.Item(f"doc{doc['id']}", (i % 4) * 3, (i // 4) * 4, 3, 4)
    #         for i, doc in enumerate(documents)
    #     ]

    #     with dashboard.Grid(layout):
    #         for doc in documents:
    #             with mui.Card(key=f"doc{doc['id']}", sx={"height": "100%"}):
    #                 mui.CardContent(
    #                     mui.Typography(doc['title'], variant="h6"),
    #                     mui.Typography(doc['description'], variant="body2", sx={"mb": 2}),
    #                     mui.Button("View", variant="contained", size="small", onClick=lambda: view_document(doc['id'])),
    #                     mui.IconButton(mui.icon.Edit, onClick=lambda: edit_document(doc['id'])),
    #                     mui.IconButton(mui.icon.Delete, onClick=lambda: delete_document(doc['id'])),
    #                 )
    # return True

# # Placeholder functions for document actions
# def view_document(doc_id):
#     st.write(f"Viewing document {doc_id}")

# def edit_document(doc_id):
#     st.write(f"Editing document {doc_id}")

# def delete_document(doc_id):
#     st.write(f"Deleting document {doc_id}")

