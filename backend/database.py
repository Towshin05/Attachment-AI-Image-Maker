import pyodbc
from typing import Optional

class Database:
    def __init__(self):
        # Update these settings according to your SQL Server configuration
        self.connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=AIImageMaker;"
            "Trusted_Connection=yes;"
        )
    
    def get_connection(self):
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def fetch_one(self, query: str, params: tuple = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
    
    def fetch_all(self, query: str, params: tuple = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
