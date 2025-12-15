from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List, Dict, Any
import csv
import json
import io
import tempfile
import os
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") != "*" else ["*"]
STATIC_DIR = os.getenv("STATIC_DIR", "static")

app = FastAPI(title="CSV Processor", version="1.0.0")

# Serve static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Graceful shutdown flag
shutdown_event = {"shutdown": False}


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\nReceived shutdown signal. Gracefully shutting down...")
    shutdown_event["shutdown"] = True
    sys.exit(0)


# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "CSV Processor"}


def find_column_case_insensitive(rows: List[Dict], target_column: str) -> str:
    """Find the actual column name in a case-insensitive way"""
    if not rows:
        return target_column
    
    available_columns = list(rows[0].keys())
    target_lower = target_column.lower()
    
    # First try exact match
    if target_column in available_columns:
        return target_column
    
    # Then try case-insensitive match
    for col in available_columns:
        if col.lower() == target_lower:
            return col
    
    # Return original if no match found
    return target_column


def process_csv_filter(rows: List[Dict], filter_column: str, filter_value: str) -> Dict[str, Any]:
    """Filter CSV rows based on column value"""
    if not rows:
        return {"rows": [], "count": 0, "columns": []}
    
    # Find the actual column name (case-insensitive)
    actual_column = find_column_case_insensitive(rows, filter_column)
    
    filtered_rows = [row for row in rows if str(row.get(actual_column, "")) == str(filter_value)]
    return {
        "rows": filtered_rows,
        "count": len(filtered_rows),
        "columns": list(rows[0].keys()) if rows else []
    }


def process_csv_transform(rows: List[Dict], transform_column: str, transform_operation: str) -> Dict[str, Any]:
    """Transform CSV column values"""
    if not rows:
        return {"rows": [], "count": 0, "columns": []}
    
    # Find the actual column name (case-insensitive)
    actual_column = find_column_case_insensitive(rows, transform_column)
    
    for row in rows:
        value = row.get(actual_column, "")
        if transform_operation == "uppercase":
            row[actual_column] = str(value).upper()
        elif transform_operation == "lowercase":
            row[actual_column] = str(value).lower()
        elif transform_operation == "trim":
            row[actual_column] = str(value).strip()
    
    return {
        "rows": rows,
        "count": len(rows),
        "columns": list(rows[0].keys()) if rows else []
    }


def process_csv_aggregate(rows: List[Dict], filter_column: str) -> Dict[str, Any]:
    """Aggregate CSV data by column"""
    if not rows:
        return {"aggregation": {}, "total_rows": 0, "column": filter_column}
    
    # Find the actual column name (case-insensitive)
    actual_column = find_column_case_insensitive(rows, filter_column)
    
    counts = {}
    for row in rows:
        key = str(row.get(actual_column, ""))
        counts[key] = counts.get(key, 0) + 1
    
    return {
        "aggregation": counts,
        "total_rows": len(rows),
        "column": actual_column
    }


def process_csv_sort(rows: List[Dict], filter_column: str) -> Dict[str, Any]:
    """Sort CSV rows by column"""
    if not rows:
        return {"rows": [], "count": 0, "columns": []}
    
    # Find the actual column name (case-insensitive)
    actual_column = find_column_case_insensitive(rows, filter_column)
    
    sorted_rows = sorted(rows, key=lambda x: str(x.get(actual_column, "")))
    return {
        "rows": sorted_rows,
        "count": len(sorted_rows),
        "columns": list(rows[0].keys()) if rows else []
    }


def process_csv_view(rows: List[Dict]) -> Dict[str, Any]:
    """View all CSV rows"""
    return {
        "rows": rows,
        "count": len(rows),
        "columns": list(rows[0].keys()) if rows else []
    }


@app.post("/api/process/csv")
async def process_csv(
    file: UploadFile = File(...),
    operation: str = Form("view"),
    filter_column: Optional[str] = Form(None),
    filter_value: Optional[str] = Form(None),
    transform_column: Optional[str] = Form(None),
    transform_operation: Optional[str] = Form(None)
):
    """
    Process CSV files with various operations:
    - view: View all rows
    - filter: Filter rows based on column value
    - transform: Transform column values
    - aggregate: Aggregate data by column
    - sort: Sort by column
    """
    try:
        # Read CSV file
        contents = await file.read()
        text_contents = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(text_contents))
        rows = list(csv_reader)
        
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Process based on operation
        if operation == "filter":
            if not filter_column or filter_value is None:
                raise HTTPException(status_code=400, detail="filter_column and filter_value required for filter operation")
            result = process_csv_filter(rows, filter_column, filter_value)
        
        elif operation == "transform":
            if not transform_column or not transform_operation:
                raise HTTPException(status_code=400, detail="transform_column and transform_operation required")
            result = process_csv_transform(rows, transform_column, transform_operation)
        
        elif operation == "aggregate":
            if not filter_column:
                raise HTTPException(status_code=400, detail="filter_column required for aggregate operation")
            result = process_csv_aggregate(rows, filter_column)
        
        elif operation == "sort":
            if not filter_column:
                raise HTTPException(status_code=400, detail="filter_column required for sort operation")
            result = process_csv_sort(rows, filter_column)
        
        else:
            # Default: return all rows
            result = process_csv_view(rows)
        
        return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file encoding. Please use UTF-8 encoded CSV files.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")


@app.post("/api/download/csv")
async def download_csv(data: dict):
    """
    Download processed CSV data
    """
    try:
        if "rows" not in data:
            raise HTTPException(status_code=400, detail="No rows data to convert to CSV. Missing 'rows' key.")
        if not data["rows"] or len(data["rows"]) == 0:
            raise HTTPException(status_code=400, detail="No rows data to convert to CSV. Empty rows array.")
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data["rows"][0].keys())
            writer.writeheader()
            writer.writerows(data["rows"])
            temp_path = f.name
        
        return FileResponse(
            temp_path,
            media_type='text/csv',
            filename=f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            headers={"Content-Disposition": f"attachment; filename=processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
    
    except HTTPException:
        # Re-raise HTTPExceptions (like our validation errors)
        raise
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format. Missing required key: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating CSV download: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    def run_server():
        """Run the server with graceful shutdown"""
        config = uvicorn.Config(
            app,
            host=HOST,
            port=PORT,
            log_level="info" if not DEBUG else "debug"
        )
        server = uvicorn.Server(config)
        
        try:
            server.run()
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
        except Exception as e:
            print(f"Server error: {e}")
            sys.exit(1)
    
    run_server()
