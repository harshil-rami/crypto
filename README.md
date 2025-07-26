# Crypto CSV Processor API

A FastAPI application that processes CSV files containing cryptocurrency data.

## Features

- Upload CSV files via API endpoint
- Store files in AWS S3
- Process CSV data and store in MongoDB
- Background processing with status tracking
- Docker and Docker Compose support

## Requirements

- Python 3.8+
- MongoDB Atlas account
- AWS S3 bucket and credentials
- Docker and Docker Compose (optional)

## Setup

1. Clone the repository
2. Copy `env.example` to `.env` and fill in your credentials:
   ```
   cp env.example .env
   ```
3. Edit the `.env` file with your MongoDB Atlas URI and AWS S3 credentials

## Running the Application

### Using Docker Compose

```bash
docker-compose up --build
```

### Without Docker

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Upload CSV

```
POST /upload-csv/
```

- Upload a CSV file with cryptocurrency data
- File should have 3 columns: coin, p/n, timestamp(IST)
- Returns a 200 response once the file is uploaded to S3
- Processing continues in the background

### Check File Status

```
GET /file-status/{file_id}
```

- Check the status of a file processing job
- Returns details about the file and processing status

## CSV Format

The CSV file should contain 3 columns in the following order:
1. Coin name
2. P/N value
3. Timestamp in IST

No header row is expected. 