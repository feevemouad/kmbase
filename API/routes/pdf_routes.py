from flask import Blueprint, request, jsonify
from models import db, PDFs, PDFMetadata
from sqlalchemy.orm import joinedload

pdf_bp = Blueprint('pdf_bp', __name__)

@pdf_bp.route('/pdfs', methods=['GET'])
def get_all_pdfs():
    pdfs = PDFs.query.all()
    pdfs_list = []
    for pdf in pdfs:
        pdf_data = {
            "user_id": pdf.user_id,
            "file_name": pdf.file_name,
            "file_path": pdf.file_path,
            }

        pdfs_list.append(pdf_data)
    return jsonify(pdfs_list)

@pdf_bp.route('/pdfs', methods=['POST'])
def upload_pdf():
    data = request.json
    new_pdf = PDFs(
        user_id=data['user_id'],
        file_name=data['file_name'],
        file_path=data['file_path']
    )
    db.session.add(new_pdf)
    db.session.commit()
    return jsonify({"message": "PDF uploaded successfully!", "pdf_id": new_pdf.id}), 201

@pdf_bp.route("/pdfs/pdfsxdescriptions", methods=["GET"])
def get_pdfs_with_descriptions():
    try:
        
        # Query using SQLAlchemy
        pdfs_with_metadata = (
            PDFs.query
            .options(joinedload(PDFs.metadata))
            .order_by(PDFs.uploaded_at.desc())
            .all()
        )
        
        # Format the results
        pdfs_with_descriptions = []
        for pdf in pdfs_with_metadata:
            pdf_data = {
                'id': pdf.id,
                'file_name': pdf.file_name,
                'file_path': pdf.file_path,
                'uploaded_at': pdf.uploaded_at.isoformat(),
                'description': pdf.metadata[0].description if pdf.metadata else None,
                'user_id': pdf.user_id,
                'file_size': pdf.metadata[0].file_size if pdf.metadata else None
            }
            pdfs_with_descriptions.append(pdf_data)
        
        return jsonify(pdfs_with_descriptions), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500    
    
@pdf_bp.route('/pdfs/<int:pdf_id>', methods=['GET'])
def get_pdf(pdf_id):
    pdfs = PDFs.query.get_or_404(pdf_id)
    return jsonify({
        'id': pdfs.id,
        'user_id': pdfs.user_id,
        'file_name': pdfs.file_name,
        'file_path': pdfs.file_path,
        'uploaded_at': pdfs.uploaded_at
    })

@pdf_bp.route('/pdfs/<int:pdf_id>/metadata', methods=['POST'])
def add_pdf_metadata(pdf_id):
    data = request.json
    new_metadata = PDFMetadata(
        pdf_id=pdf_id,
        description=data['description'],
        file_size=data['file_size']
    )
    db.session.add(new_metadata)
    db.session.commit()
    return jsonify({"message": "PDF metadata added successfully!"}), 201

@pdf_bp.route('/pdfs/<int:pdf_id>/metadata', methods=['GET'])
def get_pdf_metadata(pdf_id):
    metadata = PDFMetadata.query.filter_by(pdf_id=pdf_id).first_or_404()
    return jsonify({
        'id': metadata.id,
        'pdf_id': metadata.pdf_id,
        'description': metadata.description,
        'file_size': metadata.file_size,
        'uploaded_at': metadata.uploaded_at
    })

@pdf_bp.route('/pdfs/<int:pdf_id>', methods=['DELETE'])
def delete_pdf(pdf_id):
    pdf = PDFs.query.get_or_404(pdf_id)
    db.session.delete(pdf)
    db.session.commit()
    return jsonify({"message": "PDF deleted successfully!"})

@pdf_bp.route('/pdfs/<int:pdf_id>/metadata/edit', methods=['PUT'])
def edit_pdf_metadata(pdf_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    pdf = PDFs.query.get(pdf_id)
    try:
        # Update PDF file name
        if 'file_name' in data:
            pdf.file_name = data['file_name']
        
        # Update or create metadata
        metadata = PDFMetadata.query.filter_by(pdf_id=pdf_id).first()
        if 'description' in data:
            metadata.description = data['description']

        db.session.commit()
        
        return jsonify({
            "message": "PDF metadata updated successfully",
            "pdf_id": pdf_id,
            "file_name": pdf.file_name,
            "description": metadata.description if metadata else new_metadata.description
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500