from database import Database
from schemas import ImageGenerationRequest
import os

class ImageCRUD:
    def __init__(self):
        self.db = Database()
    
    def save_generation(self, request: ImageGenerationRequest, image_path: str, model_used: str):
        """
        Save a generated image record to the database.
        Returns the inserted ImageID.
        """
        query = """
        INSERT INTO ImageGenerations 
        (UserID, Prompt, NegativePrompt, ImagePath, ModelUsed, Width, Height, Steps)
        OUTPUT INSERTED.ImageID
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (
                request.user_id,
                request.prompt,
                request.negative_prompt,
                image_path,
                model_used,
                request.width,
                request.height,
                request.steps
            ))
            result = cursor.fetchone()  # fetch the inserted ImageID
            conn.commit()
        finally:
            cursor.close()

        return result[0] if result else None

    def delete_generation(self, image_id: int):
        """
        Delete an image record from the database and remove the file from filesystem.
        """
        # First, get the image path
        query_get = "SELECT ImagePath FROM ImageGenerations WHERE ImageID = ?"
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query_get, (image_id,))
            result = cursor.fetchone()
        finally:
            cursor.close()

        if not result:
            return False

        # Delete from database
        query_delete = "DELETE FROM ImageGenerations WHERE ImageID = ?"
        cursor = conn.cursor()
        try:
            cursor.execute(query_delete, (image_id,))
            conn.commit()
        finally:
            cursor.close()

        # Delete file from filesystem
        try:
            file_path = os.path.join("generated_images", result[0])
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

        return True

    def get_user_history(self, user_id: int, limit: int = 10):
        """
        Get recent image generations for a user.
        """
        query = """
        SELECT TOP (?) 
            ImageID, Prompt, ImagePath, GeneratedAt, ModelUsed
        FROM ImageGenerations
        WHERE UserID = ?
        ORDER BY GeneratedAt DESC
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (limit, user_id))
            rows = cursor.fetchall()
        finally:
            cursor.close()
        return rows

    def get_all_generations(self, limit: int = 20):
        """
        Get recent image generations from all users.
        """
        query = """
        SELECT TOP (?)
            ig.ImageID, ig.Prompt, ig.ImagePath, ig.GeneratedAt, u.Username
        FROM ImageGenerations ig
        INNER JOIN Users u ON ig.UserID = u.UserID
        ORDER BY ig.GeneratedAt DESC
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
        finally:
            cursor.close()
        return rows

    def get_generation_by_id(self, image_id: int):
        """
        Get a single image generation record by ID.
        """
        query = """
        SELECT ImageID, Prompt, ImagePath, GeneratedAt, Width, Height, Steps
        FROM ImageGenerations
        WHERE ImageID = ?
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (image_id,))
            row = cursor.fetchone()
        finally:
            cursor.close()
        return row

