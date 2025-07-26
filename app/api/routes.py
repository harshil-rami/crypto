from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import io
from datetime import datetime
from bson.objectid import ObjectId
import logging
from ..core.s3 import upload_to_s3
from ..core.mongo import get_db, get_files_collection, get_crypto_collection
from ..core.processor import process_csv_file

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload-csv/")
async def upload_csv(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    db=Depends(get_db),
    files_collection=Depends(get_files_collection),
    crypto_collection=Depends(get_crypto_collection)
):
    """
    Upload a CSV file, save to S3, and process the data in the background
    """
    try:
        # Check if MongoDB is available
        if files_collection is None or crypto_collection is None:
            return JSONResponse(
                status_code=503,
                content={
                    "message": "MongoDB connection not available. File will be uploaded to S3 only.",
                    "status": "s3_only"
                }
            )
            
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_filename = f"uploads/{timestamp}_{file.filename}"
        
        # Read file content
        file_content = await file.read()
        
        # Upload to S3
        s3_path = await upload_to_s3(io.BytesIO(file_content), s3_filename)
        
        # Save file metadata to MongoDB
        file_doc = {
            "original_filename": file.filename,
            "s3_path": s3_path,
            "status": "uploaded",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = await files_collection.insert_one(file_doc)
        file_id = str(result.inserted_id)
        
        # Start background processing
        background_tasks.add_task(
            process_csv_file, 
            file_id, 
            s3_path, 
            files_collection, 
            crypto_collection
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded successfully to S3. Processing started in background.",
                "file_id": file_id,
                "status": "uploaded"
            }
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/file-status/{file_id}")
async def get_file_status(
    file_id: str,
    files_collection=Depends(get_files_collection)
):
    """
    Get the status of a file processing job
    """
    try:
        if files_collection is None:
            raise HTTPException(status_code=503, detail="MongoDB connection not available")
            
        file_doc = await files_collection.find_one({"_id": ObjectId(file_id)})
        if not file_doc:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "file_id": str(file_doc["_id"]),
            "original_filename": file_doc["original_filename"],
            "status": file_doc["status"],
            "created_at": file_doc["created_at"],
            "updated_at": file_doc["updated_at"],
            "records_processed": file_doc.get("records_processed"),
            "error": file_doc.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error getting file status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting file status: {str(e)}") 