from flask import Blueprint, request, jsonify
from models import db, PDFs, PDFMetadata

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
    return jsonify({"message": "PDF uploaded successfully!"}), 201

@pdf_bp.route('/pdfs/<int:pdf_id>', methods=['GET'])
def get_pdf(pdf_id):
    pdf = PDFs.query.get_or_404(pdf_id)
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
