import os
import uuid
import requests
import json
from flask import request, jsonify
import logging
from app.utils.image_helper import is_valid_image
from app.model.face_data import FaceData         
from app.services.gcs_service import GCSService 
import base64
from datetime import datetime


FACE_RECOGNITION_API_BASE = "http://localhost:8000"

class FaceController:
    # Error message constants
    INTERNAL_SERVER_ERROR = "Internal server error"
    FACE_IMAGE_REQUIRED = "face_image required"
    FACE_IMAGE_ID_REQUIRED = "face_image_id required"

    @staticmethod
    def validate_face_image():
        # ADD input validation
        if 'face_image' not in request.files:
            return jsonify({"status": 400, "message": FaceController.FACE_IMAGE_REQUIRED}), 400

        image = request.files['face_image']

        is_ok, err_msg = is_valid_image(image)
        if not is_ok:
            return jsonify({"status": 400, "message": err_msg}), 400
        
        try:
            # FIX: Use image.seek(0) instead of image.stream.seek(0)
            image.seek(0)

            response = requests.post(
                f"{FACE_RECOGNITION_API_BASE}/validate_face_image",
                files={'file': (image.filename, image.read(), image.mimetype)},  # FIX: Use image.read()
                timeout=30
            )
            return jsonify(response.json()), response.status_code

        except Exception as e:
            logging.error(f"Error calling face-recognition API: {e}")
            return jsonify({"status": 500, "message": FaceController.INTERNAL_SERVER_ERROR}), 500
        
    @staticmethod
    def add_face():
        """Add face dengan smart duplicate checking"""
        try:
            # FIX: Get user_id properly
            user_id = request.current_user.get('admin_id')
            if not user_id:
                return jsonify({"status": 401, "message": "User ID not found in token"}), 401

            data = request.form
            name = data.get('name')
            image = request.files.get('image')

            if not name or not image:
                return jsonify({
                    'status': 400, 
                    'message': 'Name and image are required'
                }), 400

            name = name.strip()
            if not name:
                return jsonify({
                    'status': 400, 
                    'message': 'Name cannot be empty'
                }), 400

            is_ok, err_msg = is_valid_image(image)
            if not is_ok:
                return jsonify({"status": 400, "message": err_msg}), 400
            
            # Step 1: Call Face Recognition API
            image.seek(0)
            image_bytes = image.read()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            payload = {
                "name": name,
                "image": base64_image
            }

            response = requests.post(
                f"{FACE_RECOGNITION_API_BASE}/register",
                json=payload,  
                timeout=30
            )

            return jsonify(response.json()), response.status_code

            if response.status_code == 409:  # Duplicate found
                return jsonify(response.json()), 409
            elif response.status_code != 200:
                return jsonify(response.json()), response.status_code
            
            # Get result from Face Recognition API
            api_result = response.json()
            face_embedding = api_result.get('embedding')  # Could be None
        
            # Step 2: Upload to GCS
            image.seek(0)  # Reset file pointer
            gcs_service = GCSService()
            gcs_result = gcs_service.upload_face_image(image, user_id, name)
            
            if not gcs_result['success']:
                return jsonify({
                    "status": 500,
                    "message": f"Upload failed: {gcs_result['error']}"
                }), 500
            
            # Step 3: Save to database (FIX: Sesuai schema)
            face_data = FaceData()
            db_result = face_data.create_face_record(
                user_id=user_id,
                image_path=gcs_result['public_url'], 
                face_embedding=json.dumps(face_embedding) if face_embedding else None,  
                is_active=1,  
                version=1     
            )

            if db_result['success']:
                return jsonify({
                    "status": 200,
                    "message": f"Face '{name}' added successfully",
                    "data": {
                        "face_image_id": db_result['face_image_id'], 
                        "user_id": user_id,
                        "name": name,
                        "image_path": gcs_result['public_url']
                    }
                }), 200
            else:
                return jsonify({
                    "status": 500,
                    "message": f"Database error: {db_result['error']}"
                }), 500

        except Exception as e:
            logging.error(f"Error adding face: {e}")
            return jsonify({"status": 500, "message": FaceController.INTERNAL_SERVER_ERROR}), 500

    @staticmethod
    def recognize_user_face():
        """Recognize user face from uploaded image"""
        try:
            if 'face_image' not in request.files:
                return jsonify({"status": 400, "message": FaceController.FACE_IMAGE_REQUIRED}), 400
            
            image = request.files['face_image']
            is_ok, err_msg = is_valid_image(image)
            if not is_ok:
                return jsonify({"status": 400, "message": err_msg}), 400
            
            image.seek(0)  # Penting sebelum dibaca
            
            response = requests.post(
                f"{FACE_RECOGNITION_API_BASE}/recognize",
                files={
                    'image': (image.filename, image.read(), image.mimetype)
                },
                timeout=30
            )
            
            # Parse response from face recognition API
            api_response = response.json()
            
            if response.status_code == 200 and api_response.get("status") == "recognized":
                
                current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                
                # Extract confidence percentage from the API response
                confidence_str = api_response.get("confidence", "0%")
                match_percentage = int(float(confidence_str.replace('%', '')))
                
                return jsonify({
                    "status": 200,
                    "is_valid": True,
                    "recognized_at": current_time,
                    "name": api_response.get("name"),
                    "match_percentage": match_percentage
                }), 200
            else:
                # Face not recognized or API error
                return jsonify({
                    "status": 400,
                    "is_valid": False,
                    "message": api_response.get("message", "Face not recognized")
                }), 200

        except Exception as e:
            logging.error(f"Error recognizing user face: {e}")
            return jsonify({"status": 500, "message": FaceController.INTERNAL_SERVER_ERROR}), 500

    @staticmethod
    def get_faces():
        """Get all faces for current user"""
        try:
            user_id = request.current_user.get('admin_id')
            
            face_data = FaceData()
            faces = face_data.get_faces_by_user(user_id) if user_id else face_data.get_all_active_faces()
            
            return jsonify({
                "status": 200,
                "message": "Faces retrieved successfully",
                "data": faces
            }), 200
            
        except Exception as e:
            logging.error(f"Error getting faces: {e}")
            return jsonify({"status": 500, "message": FaceController.INTERNAL_SERVER_ERROR}), 500
        
    @staticmethod
    def delete_face():
        """Soft delete face"""
        try:
            face_image_id = request.args.get('face_image_id')
            if not face_image_id:
                return jsonify({"status": 400, "message": FaceController.FACE_IMAGE_ID_REQUIRED}), 400
            
            face_data = FaceData()
            result = face_data.soft_delete_face(face_image_id)
            
            if result['success']:
                return jsonify({
                    "status": 200,
                    "message": "Face deleted successfully"
                }), 200
            else:
                return jsonify({
                    "status": 500,
                    "message": result['error']
                }), 500
                
        except Exception as e:
            logging.error(f"Error deleting face: {e}")
            return jsonify({"status": 500, "message": FaceController.INTERNAL_SERVER_ERROR}), 500