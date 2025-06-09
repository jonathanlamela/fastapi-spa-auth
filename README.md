# FastAPI SPA Auth

A starter project for building a Single Page Application (SPA) with authentication using FastAPI as the backend.

## Features

- FastAPI backend for API and authentication
- JWT-based authentication
- Ready for integration with modern frontend frameworks (React, Vue, etc.)
- User registration, login, and protected routes
- Easily extendable for your needs

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
git clone https://github.com/yourusername/fastapi-spa-auth.git
cd fastapi-spa-auth
pip install -r requirements.txt
```

### Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Project Structure

```
fastapi-spa-auth/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── auth.py
│   └── ...
├── requirements.txt
└── README.md
```

## Usage

- Register a new user via `/register`
- Login via `/login` to receive a JWT token
- Access protected endpoints with the token (eg. `/status`)

## License

This project is licensed under the MIT License.
