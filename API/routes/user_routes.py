from flask import Blueprint, request, jsonify
from models import db, Users
import bcrypt

def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['GET'])
def get_all_users():
    users = Users.query.all()
    users_list = []
    for user in users:
        user_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'password_hash': user.password_hash,
            'email': user.email
        }
        users_list.append(user_data)
    return jsonify(users_list)

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    hashed_password = _hash(data['password'])
    new_user = Users(
        username=data['username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        password_hash=hashed_password,
        email=data['email'],
        role=data['role']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully!"}), 201

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

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    user = Users.query.get_or_404(user_id)
    user.username = data.get('username', user.username)
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    if 'password' in data:
        user.password_hash = _hash(data['password'])
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    db.session.commit()
    return jsonify({"message": "User updated successfully!"})

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully!"})
