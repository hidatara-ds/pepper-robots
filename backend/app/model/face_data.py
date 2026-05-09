import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
import uuid

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH", "pepper_robot.db")

class FaceData:
    
    @staticmethod
    def get_db_connection():
        """Get database connection"""
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_face_record(self, user_id, image_path, base64_image, is_active=True, version=1):
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                INSERT INTO Face_Data (
                    user_id, image_path, is_active, 
                    version, created_at, updated_at,
                    face_image_base64

                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, 
                image_path, 
                1 if bool(is_active) else 0,
                version,
                current_time,
                current_time,
                base64_image
            ))

            conn.commit()
            face_image_id = cursor.lastrowid
            return {
                'success': True,
                'face_image_id': face_image_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def get_all_active_faces(self):
        """Get all active faces"""
        conn = self.get_db_connection()
        try:
            faces = conn.execute('''
                SELECT fd.*, u.name as user_name
                FROM Face_Data fd
                LEFT JOIN User u ON fd.user_id = u.user_id
                WHERE fd.is_active = 1 AND fd.deleted_at IS NULL
                ORDER BY fd.created_at DESC
            ''').fetchall()
            
            return [dict(face) for face in faces]
            
        finally:
            conn.close()
    
    def get_faces_by_user(self, user_id):
        """Get faces by user_id"""
        conn = self.get_db_connection()
        try:
            faces = conn.execute('''
                SELECT fd.*, u.name as user_name
                FROM Face_Data fd
                LEFT JOIN User u ON fd.user_id = u.user_id
                WHERE fd.user_id = ? AND fd.is_active = 1 AND fd.deleted_at IS NULL
                ORDER BY fd.created_at DESC
            ''', (user_id,)).fetchall()
            
            return [dict(face) for face in faces]
            
        finally:
            conn.close()
    
    def get_face_by_id(self, face_image_id):
        """Get face by face_image_id"""
        conn = self.get_db_connection()
        try:
            face = conn.execute('''
                SELECT fd.*, u.name as user_name
                FROM Face_Data fd
                LEFT JOIN User u ON fd.user_id = u.user_id
                WHERE fd.face_image_id = ? AND fd.is_active = 1 AND fd.deleted_at IS NULL
            ''', (face_image_id,)).fetchone()
            
            return dict(face) if face else None
            
        finally:
            conn.close()
    
    def soft_delete_face(self, face_image_id):
        """Soft delete face by setting deleted_at timestamp"""
        conn = self.get_db_connection()
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE Face_Data 
                SET is_active = 0, deleted_at = ?, updated_at = ?
                WHERE face_image_id = ?
            ''', (current_time, current_time, face_image_id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                return {'success': True}
            else:
                return {'success': False, 'error': 'Face not found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
     
    def increment_version(self, face_image_id):
        """Increment version number for a face record"""
        conn = self.get_db_connection()
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            conn.execute('''
                UPDATE Face_Data 
                SET version = version + 1, updated_at = ?
                WHERE face_image_id = ?
            ''', (current_time, face_image_id))
            
            conn.commit()
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()

    @staticmethod
    def get_face_image_base64_by_name(user_name):
        """Get face image base64 by user name"""
        conn = FaceData.get_db_connection()
        try:
            face = conn.execute('''
                SELECT face_image_base64 
                FROM Face_Data fd
                LEFT JOIN User u ON fd.user_id = u.user_id
                WHERE u.name = ? AND fd.is_active = 1 AND fd.deleted_at IS NULL
            ''', (user_name,)).fetchone()
            
            return face['face_image_base64'] if face else None
        finally:
            conn.close()
