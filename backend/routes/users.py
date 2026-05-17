from flask import Blueprint, request, jsonify
from middleware import token_required, admin_required
import mysql.connector
from config import Config

bp = Blueprint('users', __name__, url_prefix='/api/users')

def get_db():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )

@bp.route('', methods=['GET'])
@token_required
@admin_required
def get_users(current_user):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT id, username, email, full_name, role FROM users")
        users = cursor.fetchall()
        
        return jsonify(users), 200
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        db.close()

@bp.route('/<int:user_id>/role', methods=['PUT'])
@token_required
@admin_required
def update_user_role(current_user, user_id):
    data = request.get_json()
    
    if not data or not data.get('role'):
        return jsonify({'error': 'Role is required'}), 400
    
    if data.get('role') not in ['admin', 'member']:
        return jsonify({'error': 'Invalid role'}), 400
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("UPDATE users SET role = %s WHERE id = %s", (data.get('role'), user_id))
        db.commit()
        
        return jsonify({'message': 'User role updated'}), 200
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        db.close()
