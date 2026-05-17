from flask import Blueprint, request, jsonify
from middleware import token_required, admin_required
import mysql.connector
from config import Config

bp = Blueprint('projects', __name__, url_prefix='/api/projects')

def get_db():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )

@bp.route('', methods=['GET'])
@token_required
def get_projects(current_user):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        if current_user['role'] == 'admin':
            cursor.execute("SELECT * FROM projects")
        else:
            cursor.execute("""
                SELECT p.* FROM projects p
                JOIN project_members pm ON p.id = pm.project_id
                WHERE pm.user_id = %s
            """, (current_user['id'],))
        
        projects = cursor.fetchall()
        return jsonify(projects), 200
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        db.close()

@bp.route('', methods=['POST'])
@token_required
@admin_required
def create_project(current_user):
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Project name is required'}), 400
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            "INSERT INTO projects (name, description, created_by) VALUES (%s, %s, %s)",
            (data.get('name'), data.get('description', ''), current_user['id'])
        )
        db.commit()
        project_id = cursor.lastrowid
        
        # Add creator as admin member
        cursor.execute(
            "INSERT INTO project_members (project_id, user_id, role) VALUES (%s, %s, 'admin')",
            (project_id, current_user['id'])
        )
        db.commit()
        
        return jsonify({'message': 'Project created', 'project_id': project_id}), 201
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        db.close()

@bp.route('/<int:project_id>', methods=['GET'])
@token_required
def get_project(current_user, project_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        project = cursor.fetchone()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user has access
        cursor.execute(
            "SELECT * FROM project_members WHERE project_id = %s AND user_id = %s",
            (project_id, current_user['id'])
        )
        
        if not cursor.fetchone() and current_user['role'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify(project), 200
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        db.close()

@bp.route('/<int:project_id>', methods=['PUT'])
@token_required
def update_project(current_user, project_id):
    data = request.get_json()
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Check permissions
        cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        project = cursor.fetchone()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if project['created_by'] != current_user['id'] and current_user['role'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        cursor.execute(
            "UPDATE projects SET name = %s, description = %s WHERE id = %s",
            (data.get('name', project['name']), 
             data.get('description', project['description']), 
             project_id)
        )
        db.commit()
        
        return jsonify({'message': 'Project updated'}), 200
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        db.close()

@bp.route('/<int:project_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_project(current_user, project_id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
        db.commit()
        
        return jsonify({'message': 'Project deleted'}), 200
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        db.close()
