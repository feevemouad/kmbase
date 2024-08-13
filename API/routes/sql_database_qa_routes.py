from flask import Blueprint, jsonify, request
from models import db, SQLDatabaseQA
from datetime import datetime

sql_database_qa_bp = Blueprint('sql_database_qa_bp', __name__)

@sql_database_qa_bp.route('/sql-database-qa', methods=['POST'])
def create_sql_database_qa():
    data = request.json
    new_qa = SQLDatabaseQA(
        user_id=data['user_id'],
        conversation=data['conversation']
    )
    db.session.add(new_qa)
    db.session.commit()
    return jsonify({"message": "SQL Database Q&A stored successfully!", "qa_id": new_qa.id}), 201

@sql_database_qa_bp.route('/sql-database-qa', methods=['GET'])
def get_all_sql_database_qa():
    qa_entries = SQLDatabaseQA.query.order_by(SQLDatabaseQA.created_at.desc()).all()
    qa_list = []
    for qa in qa_entries:
        qa_data = {
            "id": qa.id,
            "user_id": qa.user_id,
            "conversation": qa.conversation,
            "created_at": qa.created_at
        }
        qa_list.append(qa_data)
    return jsonify(qa_list)

@sql_database_qa_bp.route('/sql-database-qa/<int:qa_id>', methods=['GET'])
def get_sql_database_qa(qa_id):
    qa = SQLDatabaseQA.query.get_or_404(qa_id)
    return jsonify({
        'id': qa.id,
        'user_id': qa.user_id,
        'conversation': qa.conversation,
        'created_at': qa.created_at
    })

@sql_database_qa_bp.route('/users/<int:user_id>/sql-database-qa', methods=['GET'])
def get_user_sql_database_qa(user_id):
    qa_entries = SQLDatabaseQA.query.filter_by(user_id=user_id).order_by(SQLDatabaseQA.created_at.desc()).all()
    qa_list = []
    for qa in qa_entries:
        qa_data = {
            "id": qa.id,
            "conversation": qa.conversation,
            "created_at": qa.created_at
        }
        qa_list.append(qa_data)
    return jsonify(qa_list)

@sql_database_qa_bp.route('/sql-database-qa/<int:qa_id>', methods=['DELETE'])
def delete_sql_database_qa(qa_id):
    qa = SQLDatabaseQA.query.get_or_404(qa_id)
    db.session.delete(qa)
    db.session.commit()
    return jsonify({"message": "SQL Database Q&A deleted successfully!"})