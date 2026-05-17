from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes import auth, projects, tasks, users
from middleware import setup_middleware

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Setup middleware
setup_middleware(app)

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(projects.bp)
app.register_blueprint(tasks.bp)
app.register_blueprint(users.bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
