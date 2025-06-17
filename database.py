import mysql.connector
from mysql.connector import Error
from typing import Generator

class Database:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',  
            'password': 'yourpassword',  
            'database': 'fastapi_db'   
        }
    
    def get_connection(self):
        """Create and return a new database connection"""
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def get_db(self) -> Generator:
        """Generator for dependency injection"""
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn and conn.is_connected():
                conn.close()


db = Database()