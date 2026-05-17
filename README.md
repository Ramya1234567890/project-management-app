# Project Management App

A full-stack web application for creating projects, assigning tasks, and tracking progress with role-based access control (Admin/Member).

## Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Database**: MySQL

## Features
- User authentication and authorization
- Role-based access control (Admin/Member)
- Create and manage projects
- Assign tasks to team members
- Track task progress with status updates
- Dashboard with project and task overview
- Real-time progress tracking

## Project Structure
```
project-management-app/
├── backend/                  # Flask backend
│   ├── app.py               # Main Flask app
│   ├── config.py            # Configuration settings
│   ├── requirements.txt      # Python dependencies
│   ├── middleware.py        # Authentication & RBAC middleware
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── tasks.py
│   │   └── users.py
│   ├── .env.example         # Environment variables example
│   └── database.sql         # Database schema
├── frontend/                # JavaScript frontend
│   ├── index.html           # Main entry point
│   ├── css/
│   │   ├── style.css        # Global styles
│   │   └── dashboard.css    # Dashboard styles
│   ├── js/
│   │   ├── api.js           # API client
│   │   ├── auth.js          # Authentication logic
│   │   ├── projects.js      # Project management
│   │   ├── tasks.js         # Task management
│   │   ├── dashboard.js     # Dashboard logic
│   │   └── utils.js         # Utility functions
│   └── pages/               # HTML pages
│       ├── login.html
│       ├── register.html
│       └── dashboard.html
├── .gitignore
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js (for frontend development)
- MySQL 5.7+

### Database Setup
```bash
# Login to MySQL
mysql -u root -p

# Run the database schema
source backend/database.sql
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Update .env with your MySQL credentials
python app.py
```

### Frontend Setup
```bash
cd frontend
# Serve using any HTTP server (e.g., Live Server extension in VS Code)
# Or use Python: python -m http.server 8000
```

The app will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### Projects
- `GET /api/projects` - Get all projects
- `POST /api/projects` - Create new project (Admin only)
- `GET /api/projects/<id>` - Get project details
- `PUT /api/projects/<id>` - Update project (Admin only)
- `DELETE /api/projects/<id>` - Delete project (Admin only)

### Tasks
- `GET /api/tasks` - Get all tasks
- `GET /api/tasks?project_id=<id>` - Get tasks for a project
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task (Admin only)

### Users
- `GET /api/users` - Get all users (Admin only)
- `PUT /api/users/<id>/role` - Update user role (Admin only)

## Usage

1. **Register** a new account at the register page
2. **Login** with your credentials
3. **Create Projects** (Admin role required)
4. **Create Tasks** and assign to team members
5. **Track Progress** via dashboard
6. **Update Task Status** as work progresses

## Default Admin Setup

To create an admin user, register an account first, then in the database:
```sql
UPDATE users SET role = 'admin' WHERE username = 'your_username';
```

## License
MIT
