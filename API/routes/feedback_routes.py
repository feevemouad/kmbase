from flask import Blueprint, request, jsonify
from models import db, Users, Feedback


feedback_bp = Blueprint('feedback_bp', __name__)

@feedback_bp.route('/feedback', methods=['POST'])
def create_feedback():
    data = request.json
    user_id = data.get('user_id')
    conversation = data.get('conversation')
    feedback_description = data.get('feedback_description')
    
    if not conversation:
        return jsonify({"message": "Conversation data is required", "status": False}), 400

    new_feedback = Feedback(
        user_id=user_id,
        conversation=conversation,
        feedback_description=feedback_description
    )
    try:
        db.session.add(new_feedback)
        db.session.commit()
        return jsonify({"message": "Feedback created successfully!","status": True}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating feedback", "status": False, "error": str(e)}), 400

@feedback_bp.route('/feedback', methods=['GET'])
def get_all_feedback():
    feedback_records = Feedback.query.all()
    feedback_list = []
    for feedback in feedback_records:
        feedback_data = {
            'id': feedback.id,
            'user_id': feedback.user_id,
            'conversation': feedback.conversation,
            'feedback_description': feedback.feedback_description,
            'created_at': feedback.created_at
        }
        feedback_list.append(feedback_data)
    return jsonify(feedback_list)

@feedback_bp.route('/feedback/<int:feedback_id>', methods=['GET'])
def get_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    return jsonify({
        'id': feedback.id,
        'user_id': feedback.user_id,
        'conversation': feedback.conversation,
        'feedback_description': feedback.feedback_description,
        'created_at': feedback.created_at
    })

@feedback_bp.route('/feedback/user/<int:user_id>', methods=['GET'])
def get_feedback_by_user(user_id):
    feedback_records = Feedback.query.filter_by(user_id=user_id).all()
    feedback_list = []
    for feedback in feedback_records:
        feedback_data = {
            'id': feedback.id,
            'user_id': feedback.user_id,
            'conversation': feedback.conversation,
            'feedback_description': feedback.feedback_description,
            'created_at': feedback.created_at
        }
        feedback_list.append(feedback_data)
    return jsonify(feedback_list)

@feedback_bp.route('/feedback/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    try:
        feedback = Feedback.query.get(feedback_id)
        db.session.delete(feedback)
        db.session.commit()
        return jsonify({"message": "PDF deleted successfully!", "status": True })
    except: 
        return jsonify({"message": "PDF not deleted", "status": False })
