from flask import Blueprint, request, jsonify  
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity  
from models import User, db  
import re  

auth_bp = Blueprint('auth', __name__)  

@auth_bp.route('/register', methods=['POST'])  
def register():  
    """  
    User Registration Endpoint  
    """  
    data = request.get_json()  
    
    # Validate input  
    username = data.get('username')  
    email = data.get('email')  
    password = data.get('password')  

    # Input validation  
    if not username or not email or not password:  
        return jsonify({"error": "Missing required fields"}), 400  

    # Email validation  
    if not User.validate_email(email):  
        return jsonify({"error": "Invalid email format"}), 400  

    # Check if user already exists  
    if User.query.filter_by(username=username).first():  
        return jsonify({"error": "Username already exists"}), 409  

    if User.query.filter_by(email=email).first():  
        return jsonify({"error": "Email already registered"}), 409  

    # Create new user  
    try:  
        new_user = User(username=username, email=email)  
        new_user.set_password(password)  
        
        db.session.add(new_user)  
        db.session.commit()  

        return jsonify({  
            "message": "User registered successfully",  
            "user": new_user.to_dict()  
        }), 201  

    except Exception as e:  
        db.session.rollback()  
        return jsonify({"error": str(e)}), 500  

@auth_bp.route('/login', methods=['POST'])  
def login():  
    """  
    User Login Endpoint  
    """  
    data = request.get_json()  
    username = data.get('username')  
    password = data.get('password')  

    if not username or not password:  
        return jsonify({"error": "Missing username or password"}), 400  

    user = User.query.filter_by(username=username).first()  

    if user and user.check_password(password):  
        # Create access token  
        access_token = create_access_token(identity=user.id)  
        return jsonify({  
            "access_token": access_token,  
            "user": user.to_dict()  
        }), 200  
    else:  
        return jsonify({"error": "Invalid credentials"}), 401  

@auth_bp.route('/profile', methods=['GET'])  
@jwt_required()  
def get_profile():  
    """  
    Get User Profile Endpoint  
    """  
    current_user_id = get_jwt_identity()  
    user = User.query.get(current_user_id)  

    if user:  
        return jsonify(user.to_dict()), 200  
    else:  
        return jsonify({"error": "User not found"}), 404