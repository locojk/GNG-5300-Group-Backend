from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router  # Import the top-level router object from the API

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",  # Frontend development URL
    "http://gng-5300-group-frontend-b2bzeef2arg4b6fu.canadacentral-01.azurewebsites.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow these origins to access the API
    allow_credentials=True, # Allow cookies and authentication headers
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allow all headers (e.g., Content-Type, Authorization)
)

# Register API routes with "/api" prefix
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the 5300 API"}

