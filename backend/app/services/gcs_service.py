import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
from google.cloud import storage
from app.model.user import User

load_dotenv()

class GCSService:
    
    def __init__(self):
        self.bucket_name = os.getenv('GCS_BUCKET_NAME', 'pepper-robot-faces')
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

        if self.credentials_path and os.path.exists(self.credentials_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
        
        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
            logging.info("GCS client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize GCS client: {e}")
            raise RuntimeError("GCS client init failed")

    def upload_face_image(self, file, user_id, name):
        """Upload face image to Google Cloud Storage"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            file_extension = os.path.splitext(file.filename)[1] or '.jpg'
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name}_{timestamp}{file_extension}"

            # Upload to GCS
            return self._upload_to_gcs(file, user_id, filename)

        except Exception as e:
            logging.error(f"Error uploading face image: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _upload_to_gcs(self, file, user_id, filename):
        """
        Upload file to Google Cloud Storage
        
        Args:
            file: File object to upload
            user_id: User ID to get user name
            filename: Generated filename for the uploaded file
            
        Returns:
            Dict with upload result (success, public_url, blob_name) or error info
        """
        try:
            # Get user information from database
            user_data = User.get_user_by_id(user_id)
            
            if user_data and user_data.get('name'):
                # Sanitize user name for folder naming: replace spaces and special chars with underscores
                # This ensures valid GCS blob paths and prevents path traversal issues
                user_name = user_data['name'].strip()
                # Replace spaces and invalid characters with underscores
                user_name = re.sub(r'[^\w\-]', '_', user_name)
                # Remove multiple consecutive underscores
                user_name = re.sub(r'_+', '_', user_name)
                # Remove leading/trailing underscores
                user_name = user_name.strip('_')
                # Fallback if name becomes empty after sanitization
                if not user_name:
                    user_name = 'unknown_user'
            else:
                user_name = 'unknown_user'
                logging.warning(f"User not found for user_id: {user_id}, using default folder name")
            
            blob_name = f"faces/{user_name}/{filename}"
            blob = self.bucket.blob(blob_name)

            file.seek(0)
            blob.upload_from_file(file, content_type=file.mimetype)

            logging.info(f"Successfully uploaded to GCS: {blob_name}")

            return {
                'success': True,
                'public_url': f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}",
                'blob_name': blob_name
            }

        except Exception as e:
            logging.error(f"Error uploading to GCS: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_face_image(self, blob_name):
        """Delete face image from GCS"""
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logging.info(f"Successfully deleted from GCS: {blob_name}")
            return {'success': True}
        except Exception as e:
            logging.error(f"Error deleting face image: {e}")
            return {'success': False, 'error': str(e)}
