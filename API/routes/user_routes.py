from flask import Blueprint, request, jsonify
from Services.HashingService import HashingService
from models import db, Users, PDFs

_hash = HashingService()
user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['GET'])
def get_all_users():
    users = Users.query.all()
    users_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'password_hash': user.password_hash,
            'role': user.role,
            'created_at': user.created_at
        }
        users_list.append(user_data)
    return jsonify(users_list)

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    hashed_password = _hash.hash_bcrypt(data['password'])
    new_user = Users(
        username=data['username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        password_hash=hashed_password,
        email=data['email'],
        role=data['role']
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating user, user may already exist", "error": str(e)}), 400

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = Users.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at
    })

@user_bp.route('/users/<string:username>', methods=['GET'])
def get_user_by_username(username):
    user = Users.query.filter_by(username=username).first_or_404()
    return jsonify({
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at
    })

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    user = Users.query.get_or_404(user_id)
    if 'username' in data:
        user.username = data.get('username', user.username)
    if 'first_name' in data:     
        user.first_name = data.get('first_name', user.first_name)
    if 'last_name' in data:       
        user.last_name = data.get('last_name', user.last_name)
    if 'password' in data:
        user.password_hash = _hash.hash_bcrypt(data['password'])
    if 'email' in data:       
        user.email = data.get('email', user.email)
    if 'role' in data:       
        user.role = data.get('role', user.role)
    db.session.commit()
    return jsonify({"message": "User updated successfully!"})

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Users.query.get(user_id)
    if user : 
        PDFs.query.filter_by(user_id=user_id).update({'user_id': 3})
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully!"})
    return jsonify({"message": "User not found!"}), 404
