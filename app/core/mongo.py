import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "crypto_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "crypto_data")
FILES_COLLECTION = os.getenv("FILES_COLLECTION", "uploaded_files")

# Create a MongoDB client with connection timeout
try:
    client = AsyncIOMotorClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    # Force a connection to verify it works
    logger.info("Connecting to MongoDB...")
    db = client[DB_NAME]
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    # Create a fallback in-memory database for development
    logger.warning("Using in-memory MongoDB for development")
    client = None
    db = None

async def get_db():
    """
    Get MongoDB database instance
    """
    if db is None:
        logger.warning("MongoDB connection not available")
    return db

async def get_crypto_collection():
    """
    Get the crypto data collection
    """
    if db is None:
        logger.warning("MongoDB connection not available")
        return None
    return db[COLLECTION_NAME]

async def get_files_collection():
    """
    Get the uploaded files collection
    """
    if db is None:
        logger.warning("MongoDB connection not available")
        return None
    return db[FILES_COLLECTION] 