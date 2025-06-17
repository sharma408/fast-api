from typing import Optional, Dict, List
from database import db

class User:
    @staticmethod
    def create(
        name: str,
        mobile: str,
        address: str,
        state: str,
        city: str,
        pincode: str,
        image: Optional[str] = None
    ) -> int:
        """Create a new user and return the user ID"""
        conn = None
        cursor = None
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO users 
            (name, mobile, address, image, state, city, pincode) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (name, mobile, address, image, state, city, pincode)
            
            cursor.execute(query, values)
            conn.commit()
            print(f"👤 User '{name}' created successfully")
            return cursor.lastrowid
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def get_all() -> List[Dict]:
        """Get all users"""
        conn = None
        cursor = None
        try:
            conn = db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            print(f"📋 Found {len(users)} users")
            return users
            
        except Exception as e:
            raise
        finally:
            if cursor:
                cursor.close()