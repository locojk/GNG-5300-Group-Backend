# GNG-5300-Group-Backend


├── README.md               # Project overview and documentation; includes setup, configuration, and usage instructions
├── api                     # API routing directory
│   ├── __init__.py         # Initializes the top-level API router
│   └── v1                  # API version 1 folder
│       ├── __init__.py     # Initializes API version 1 routes
│       ├── health          # Health check-related routes
│       │   ├── __init__.py
│       │   └── health.py   # Endpoint for health checks to verify system availability
│       └── user            # User-related routes
│           ├── __init__.py
│           └── user.py     # User management API endpoints (e.g., registration, login)
├── daos                    # Data Access Object (DAO) layer for database interactions
│   ├── __init__.py
│   ├── mongodb_client.py   # MongoDB client configuration and basic operations
│   └── user                # User-specific DAOs
│       ├── __init__.py
│       └── users_dao.py    # User DAO for CRUD operations related to user data
├── env_config              # Environment configuration directory containing .env files
├── main.py                 # Entry point of the application; initializes FastAPI and sets up API routing
├── resources               # Directory for auxiliary resources
│   └── __init__.py
├── schema                  # Directory for JSON schema files used in validation
│   └── user
│       └── users.schema.json # JSON schema for user data validation
├── scripts                 # Directory for scripts and utilities (e.g., database migration or setup scripts)
│   └── __init__.py
├── services                # Business logic layer for handling core application functions
│   └── user                # User-related services
│       ├── __init__.py
│       ├── auth_service.py # Handles user authentication and token management
│       ├── user_service.py # Main user management logic (e.g., profile updates, password changes)
│       └── validation.py   # Validation schemas for user-related data (e.g., registration, login)
└── utils                   # Utility functions and helpers for various application features
    ├── auth_helpers.py     # Helpers for authentication, e.g., token generation
    ├── decorators.py       # Custom decorators for functionality (e.g., route protection)
    ├── email_helpers.py    # Email-related helper functions (e.g., sending reset emails)
    ├── env_loader.py       # Loads environment variables based on OS and hostname
    ├── http_client.py      # HTTP client helper for making HTTP requests
    └── logger.py           # Logging setup and configurations




1. install requirements.txt


python3 -m venv venv

MACOS:
source venv/bin/activate

WIN:
.\venv\Scripts\activate


deactivate


test:
python -m unittest discover tests

tree -I "venv|*.pyc|__pycache__"

see error message

python -c "import app"

## run server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug


## jenkins docker



