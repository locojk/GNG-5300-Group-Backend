from fastapi import FastAPI
from api import router as api_router  # Import the top-level router object from the API

app = FastAPI()

# Register API routes with "/api" prefix
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the 5300 API"}
