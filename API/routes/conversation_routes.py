from datetime import datetime
from flask import Blueprint, jsonify, request
from models import db, Conversation

conversation_bp = Blueprint('conversation_bp', __name__)

@conversation_bp.route('/conversations', methods=['POST'])
def create_conversation():
    data = request.json
    new_conversation = Conversation(
        user_id=data['user_id'],
        conversation=data['conversation']
    )
    db.session.add(new_conversation)
    db.session.commit()
    return jsonify({"message": "Conversation created successfully!", "conversation_id": new_conversation.id}), 201

@conversation_bp.route('/conversations/<int:conversation_id>', methods=['PUT'])
def update_conversation(conversation_id):
    data = request.json
    conversation = Conversation.query.get_or_404(conversation_id)
    conversation.conversation = data['conversation']
    conversation.last_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Conversation updated successfully!"}), 200

@conversation_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    return jsonify({
        'id': conversation.id,
        'user_id': conversation.user_id,
        'conversation': conversation.conversation,
        'created_at': conversation.created_at,
        'last_updated': conversation.last_updated
    })

@conversation_bp.route('/conversations', methods=['GET'])
def get_all_conversations():
    conversations = Conversation.query.order_by(Conversation.created_at.desc()).all()
    conversations_list = []
    for conv in conversations:
        conv_data = {
            "id": conv.id,
            "user_id": conv.user_id,
            "conversation": conv.conversation,
            "created_at": conv.created_at,
            "last_updated": conv.last_updated

        }
        conversations_list.append(conv_data)
    return jsonify(conversations_list)

@conversation_bp.route('/conversations/<int:conversation_id>', methods=["DELETE"])
def delete_conversation(conversation_id):
    try:
        conversation = Conversation.query.get(conversation_id)
        db.session.delete(conversation)
        db.session.commit()
        return jsonify({"message": "conversation deleted successfully!", "status": True })
    except: 
        return jsonify({"message": "conversation not deleted", "status": False })
