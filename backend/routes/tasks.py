from flask import Blueprint, request, jsonify
from middleware import token_required, admin_required
import mysql.connector
from config import Config

bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

def get_db():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )

@bp.route('', methods=['GET'])
@token_required
def get_tasks(current_user):
    project_id = request.args.get('project_id')
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        if project_id:
            cursor.execute("SELECT * FROM tasks WHERE project_id = %s", (project_id,))
        else:
            cursor.execute("SELECT * FROM tasks")
        
        tasks = cursor.fetchall()
        return jsonify(tasks), 200
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        db.close()

@bp.route('', methods=['POST'])
@token_required
def create_task(current_user):
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('project_id'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            """INSERT INTO tasks 
            (project_id, title, description, assigned_to, status, priority, due_date, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (data.get('project_id'), data.get('title'), data.get('description', ''),
             data.get('assigned_to'), data.get('status', 'todo'),
             data.get('priority', 'medium'), data.get('due_date'), current_user['id'])
        )
        db.commit()
        
        return jsonify({'message': 'Task created', 'task_id': cursor.lastrowid}), 201
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        db.close()

@bp.route('/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    data = request.get_json()
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        task = cursor.fetchone()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check permissions
        if task['created_by'] != current_user['id'] and task['assigned_to'] != current_user['id'] and current_user['role'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        updates = []
        params = []
        
        for field in ['title', 'description', 'assigned_to', 'status', 'priority', 'due_date']:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])
        
        if updates:
            params.append(task_id)
            cursor.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s", params)
            db.commit()
            
            # Log progress change
            if 'status' in data and data['status'] != task['status']:
                cursor.execute(
                    "INSERT INTO progress_logs (task_id, old_status, new_status, changed_by) VALUES (%s, %s, %s, %s)",
                    (task_id, task['status'], data['status'], current_user['id'])
                )
                db.commit()
        
        return jsonify({'message': 'Task updated'}), 200
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        db.close()

@bp.route('/<int:task_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_task(current_user, task_id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        db.commit()
        
        return jsonify({'message': 'Task deleted'}), 200
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        db.close()
