from fastapi import FastAPI
from dotenv import load_dotenv
import logging
from .api.routes import router

# Load environment variables directly
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Crypto CSV Processor API",
    description="API for processing CSV files with cryptocurrency data",
    version="1.0.0",
)

# Include API routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Crypto CSV Processor API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 