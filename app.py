from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import mysql.connector
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Annotated

app = FastAPI()

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'yourpassword',
    'database': 'fastapi_db'
}

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {err}")

def validate_file(file: UploadFile):
    if not file.filename:
        raise HTTPException(400, detail="No file uploaded")
    
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, detail="Invalid file type. Allowed: png, jpg, jpeg, gif")
    
    file.file.seek(0, 2)
    if file.file.tell() > MAX_FILE_SIZE:
        raise HTTPException(400, detail="File too large (max 10MB)")
    file.file.seek(0)

@app.post("/")
async def create_user(
    name: Annotated[str, Form()],
    mobile: Annotated[str, Form()],
    address: Annotated[str, Form()],
    state: Annotated[str, Form()],
    city: Annotated[str, Form()],
    pincode: Annotated[str, Form()],
    images: Annotated[UploadFile, File()] = None
):
    connection = None
    cursor = None
    try:
        image_name = "no-image.jpg"
        if images:
            validate_file(images)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_ext = images.filename.split('.')[-1].lower()
            image_name = f"{timestamp}_{name.replace(' ', '_')}.{file_ext}"
            image_path = Path(UPLOAD_DIR) / image_name
            
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(images.file, buffer)

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO users 
        (name, mobile, address, images, state, city, pincode) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (name, mobile, address, image_name, state, city, pincode)
        
        cursor.execute(query, values)
        connection.commit()
        user_id = cursor.lastrowid

        return {
            "message": "User created successfully",
            "user_id": user_id,
            "image": image_name
        }

    except mysql.connector.Error as err:
        if connection:
            connection.rollback()
        raise HTTPException(500, detail=f"Database error: {err}")
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)