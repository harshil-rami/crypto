import pandas as pd
import io
from datetime import datetime
from bson.objectid import ObjectId
import logging
from .s3 import get_from_s3

# Configure logging
logger = logging.getLogger(__name__)

async def process_csv_file(file_id, s3_path, files_collection, crypto_collection):
    """
    Background task to process the CSV file from S3 and save data to MongoDB
    
    Args:
        file_id: MongoDB ID of the file document
        s3_path: S3 path of the uploaded file
        files_collection: MongoDB collection for file metadata
        crypto_collection: MongoDB collection for crypto data
    """
    try:
        logger.info(f"Starting to process file {file_id} from S3 path: {s3_path}")
        
        # Check if MongoDB collections are available
        if files_collection is None or crypto_collection is None:
            logger.error("MongoDB collections not available, cannot process file")
            return
            
        # Update file status to processing
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"status": "processing", "updated_at": datetime.now()}}
        )
        
        # Get file from S3
        file_content = await get_from_s3(s3_path)
        
        # Parse CSV
        df = pd.read_csv(io.BytesIO(file_content), header=None)
        
        # Check if CSV has the expected format (3 columns)
        if len(df.columns) != 3:
            await files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {"$set": {
                    "status": "failed", 
                    "error": "CSV file does not have 3 columns", 
                    "updated_at": datetime.now()
                }}
            )
            return
        
        # Process each row and insert into MongoDB
        documents = []
        for _, row in df.iterrows():
            document = {
                "coin": row[0],
                "pn": row[1],  # p/n value
                "timestamp": row[2],
                "created_at": datetime.now(),
                "file_id": file_id
            }
            documents.append(document)
        
        if documents:
            # Insert all documents
            await crypto_collection.insert_many(documents)
            
            # Update file status to completed
            await files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {"$set": {
                    "status": "completed", 
                    "records_processed": len(documents),
                    "updated_at": datetime.now()
                }}
            )
            logger.info(f"Successfully processed {len(documents)} records from file {file_id}")
        else:
            await files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {"$set": {
                    "status": "completed", 
                    "records_processed": 0, 
                    "updated_at": datetime.now()
                }}
            )
            logger.info(f"No records found in file {file_id}")
            
    except Exception as e:
        logger.error(f"Error processing file {file_id}: {str(e)}")
        # Update file status to failed if MongoDB is available
        if files_collection is not None:
            try:
                await files_collection.update_one(
                    {"_id": ObjectId(file_id)},
                    {"$set": {
                        "status": "failed", 
                        "error": str(e), 
                        "updated_at": datetime.now()
                    }}
                )
            except Exception as update_error:
                logger.error(f"Could not update file status: {str(update_error)}") 