import base64
import os
import json
import requests
from flask import request, jsonify
import logging
from app.model.user import User
from app.utils.image_helper import is_valid_image
from app.utils.image_compression import compress_image, get_image_info
from app.model.face_data import FaceData         

FACE_RECOGNITION_API_BASE = "http://localhost:8000"


class UserController:
    @staticmethod
    def get_user_by_id(user_id: str):
        """
        Get user by user_id
        
        Args:
            user_id: User ID from URL parameter
            
        Returns:
            JSON response with user data or error message
        """
        try:
            # Get user by ID using the model
            user_data = User.get_user_by_id(user_id)
            
            # Check if user exists
            if user_data is None:
                return jsonify({
                    "status": 404,
                    "message": "User doesn't exists"
                }), 404
            
            # Return user data
            return jsonify({
                "user_id": user_data['user_id'],
                "name": user_data['name'],
                "created_at": user_data['created_at'],
                "updated_at": user_data['updated_at']
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": 500,
                "message": f"Internal server error: {str(e)}"
            }), 500
    
    @staticmethod
    def update_user_name(user_id: str):
        """
        Update user name
        
        Args:
            user_id: User ID from URL parameter
            
        Returns:
            JSON response with updated user data or error message
        """
        try:
            # Get request data
            data = request.get_json()
            
            # Validate request body
            if not data:
                return jsonify({
                    "status": 400,
                    "message": "Request body is required"
                }), 400
            
            # Get name from request body
            name = data.get('name')
            if not name:
                return jsonify({
                    "status": 400,
                    "message": "Name is required"
                }), 400
            
            # Update user name using model
            result = User.update_user_name(user_id, name)
            
            # Check if update was successful
            if result['success']:
                return jsonify({
                    "status": result['status'],
                    "name": result['name'],
                    "updated_at": result['updated_at']
                }), result['status']
            else:
                return jsonify({
                    "status": result['status'],
                    "message": result['message']
                }), result['status']
                
        except Exception as e:
            return jsonify({
                "status": 500,
                "message": f"Internal server error: {str(e)}"
            }), 500
    
    @staticmethod
    def delete_user(user_id: str):
        """
        Soft delete user
        
        Args:
            user_id: User ID from URL parameter
            
        Returns:
            JSON response with deletion status or error message
        """
        try:
            # Soft delete user using model
            result = User.soft_delete_user(user_id)
            
            # Check if deletion was successful
            if result['success']:
                return jsonify({
                    "status": result['status'],
                    "deleted_at": result['deleted_at']
                }), result['status']
            else:
                return jsonify({
                    "status": result['status'],
                    "message": result['message']
                }), result['status']
                
        except Exception as e:
            return jsonify({
                "status": 500,
                "message": f"Internal server error: {str(e)}"
            }), 500

    @staticmethod
    def get_identities():
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))

            data, pagination = User.get_active_identities(page, limit)

            return jsonify({
                "data": data,
                "pagination": pagination
            }), 200

        except Exception as e:
            return jsonify({
                "message": "Internal server error",
                "error": str(e)
            }), 500
        
    @staticmethod
    def _validate_registration_input(name, face_image):
        """Validate input for user registration"""
        if not name or not face_image:
            return False, "Name and face_image are required"
        
        name = name.strip()
        if not name or len(name) < 2:
            return False, "Name must be at least 2 characters long"
        
        is_ok, err_msg = is_valid_image(face_image)
        if not is_ok:
            return False, err_msg
            
        return True, name

    @staticmethod
    def _compress_image_for_upload(face_image):
        """Compress image and return buffer with info"""
        original_info = get_image_info(face_image)
        logging.info(f"Original image: {original_info}")
        
        try:
            compressed_buffer, compressed_filename = compress_image(face_image)
            logging.info(f"Image compressed successfully: {compressed_filename}")
            return compressed_buffer, compressed_filename, original_info
        except ValueError as e:
            raise ValueError(f"Image compression failed: {str(e)}")

    @staticmethod
    def _validate_face_with_api(compressed_buffer, compressed_filename):
        """Validate face with Face Recognition API"""
        compressed_buffer.seek(0)
        response = requests.post(
            f"{FACE_RECOGNITION_API_BASE}/recognize",
            files={'file': (compressed_filename, compressed_buffer.read(), 'image/jpeg')},
            timeout=30
        )
        
        if response.status_code != 200:
            raise ValueError(f"Face validation failed: {response.text}")
            
        api_result = response.json()
        if api_result.get('status') == 'recognized':
            raise ValueError("Face already registered")
            
        return api_result.get('embedding')

    @staticmethod
    def _create_compressed_file_object(buffer, filename):
        """Create file-like object for GCS upload"""
        class CompressedFile:
            def __init__(self, buffer, filename, mimetype='image/jpeg'):
                self.buffer = buffer
                self.filename = filename
                self.mimetype = mimetype
            
            def seek(self, pos):
                return self.buffer.seek(pos)
            
            def tell(self):
                return self.buffer.tell()
            
            def read(self, size=-1):
                return self.buffer.read(size)
            
            def readline(self):
                return self.buffer.readline()
            
            def readlines(self):
                return self.buffer.readlines()
        
        return CompressedFile(buffer, filename)

    @staticmethod
    def register_identity():
        """Register new identity with name and face image"""
        try:
            # Get and validate input
            name = request.form.get('name')
            face_image = request.files.get('face_image')

            is_valid, result = UserController._validate_registration_input(name, face_image)
            if not is_valid:
                return jsonify({"status": 400, "message": result}), 400
            name = result

            # Compress image
            try:
                compressed_buffer, compressed_filename, original_info = UserController._compress_image_for_upload(face_image)
            except ValueError as e:
                return jsonify({"status": 400, "message": str(e)}), 400
            

            # Check if face already exists in recognition system
            try:
                compressed_buffer.seek(0)  # Kembali ke awal

                recognize_response = requests.post(
                    f"{FACE_RECOGNITION_API_BASE}/recognize",
                    files={
                        "image": (compressed_filename, compressed_buffer.read(), "image/jpeg")
                    },
                    timeout=30
                )

                print(f"Recognize response: {recognize_response.status_code} - {recognize_response.text}")

                if recognize_response.status_code == 200:
                    recognize_data = recognize_response.json()
                    print(f"Face recognition response: {recognize_data}")
                    if recognize_data.get('status') == 'recognized':
                        return jsonify({
                            "status": 400, 
                            "message": "Wajah sudah terdaftar dalam sistem. Tidak dapat mendaftarkan wajah yang sama."
                        }), 400

            except Exception as e:
                logging.error(f"Error checking face recognition: {e}")
                return jsonify({"status": 400, "message": f"Gagal mengecek wajah di sistem: {str(e)}"}), 400
            
            # Create user
            user_result = User.create_user(name)
            if not user_result['success']:
                return jsonify({"status": 400, "message": user_result['message']}), 400

            user_id = user_result['user_id']
            created_at = user_result['created_at']

            try:
                # Register face to recognition system (local storage)
                compressed_buffer.seek(0)  # Kembali ke awal
                image_bytes = compressed_buffer.read()
                base64_image = base64.b64encode(image_bytes).decode('utf-8')

                register_payload = {
                    "name": name,
                    "image": base64_image
                }

                face_api_response = requests.post(
                    f"{FACE_RECOGNITION_API_BASE}/register",
                    json=register_payload,
                    timeout=30
                )

                if face_api_response.status_code != 200:
                    raise ValueError(f"Gagal mendaftarkan wajah ke face-recognition: {face_api_response.text}")

                # Parse response from local face recognition API
                response_data = face_api_response.json()
                logging.info(f"Face registration API success: {response_data}")
                print(f"Face registration API success: {response_data}")

                # Get local path from the response (instead of GCS URL)
                local_path = response_data.get('local_path', '')
                base64_image = response_data.get('image_base64', '')

                # Save face data to database with local path
                face_data = FaceData()
                face_data_result = face_data.create_face_record(
                    user_id=user_id,
                    image_path=local_path,  
                    is_active=True,
                    base64_image=base64_image,
                    version=1
                )

                if not face_data_result['success']:
                    User.hard_delete_user(user_id)
                    # If face data creation failed, delete the local file
                    if local_path and os.path.exists(local_path):
                        try:
                            os.remove(local_path)
                            logging.info(f"Deleted local file: {local_path}")
                        except Exception as delete_error:
                            logging.error(f"Failed to delete local file: {delete_error}")
                    return jsonify({"status": 400, "message": f"Failed to save face data: {face_data_result['error']}"}), 400

            except Exception as e:
                User.hard_delete_user(user_id)
                return jsonify({"status": 400, "message": f"Gagal daftarkan wajah ke face-recognition: {str(e)}"}), 400

            # Return success with local path
            return jsonify({
                "name": name,
                "created_at": created_at,
                "face_image_path": local_path  # Return local path instead of GCS URL
            }), 200

        except Exception as e:
            logging.error(f"Error registering identity: {e}")
            return jsonify({"status": 500, "message": "Internal server error"}), 500