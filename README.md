# User Management API

A backend **user authentication and user management system** built with FastAPI.

---

## Features

### Implemented
- User registration (email + password)
- Email verification via token
- Password hashing
- Async PostgreSQL database
- Alembic migrations

### Planned
- Login (email + password)
- Password reset (forgot password)
- Google OAuth authentication
- JWT-based access tokens

---

## Tech Stack
- FastAPI
- PostgreSQL
- SQLModel (async)
- Alembic
- JWT
- FastAPI-Mail

---

## How to Run the Project

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd UserManagement
Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Environment variables

Create a .env file using .env.example as reference.

5. Run database migrations
alembic upgrade head

6. Start the server
uvicorn main:app --reload


Server:

http://127.0.0.1:8000


API Docs:

http://127.0.0.1:8000/docs
