# Reader API

A FastAPI-based REST API for managing reading projects and content.

## Features

- User authentication with JWT tokens
- Project management
- Document management within projects
- Secure password hashing
- SQLAlchemy ORM for database operations
- Pydantic models for data validation

## Prerequisites

- Python 3.7+
- PostgreSQL database
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Reader
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/reader_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
```

5. Initialize the database:
```bash
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
```

## Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/v1/token` - Get access token

### Users
- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/me/` - Get current user

### Projects
- `POST /api/v1/projects/` - Create new project
- `GET /api/v1/projects/` - List user's projects
- `GET /api/v1/projects/{project_id}` - Get project details

### Documents
- `POST /api/v1/documents/` - Create new document
- `GET /api/v1/documents/` - List all documents
- `GET /api/v1/projects/{project_id}/documents/` - List project documents

## Security

- All endpoints except `/token` and `/users/` require authentication
- Passwords are hashed using bcrypt
- JWT tokens are used for authentication
- CORS is enabled for development (configure appropriately for production)

## Development

To run tests:
```bash
pytest
```

To check code style:
```bash
flake8
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
