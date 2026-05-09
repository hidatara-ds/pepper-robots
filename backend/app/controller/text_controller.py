from flask import jsonify, request, g
from app.controller.config_controller import ConfigController
from app.model.kamus_bahasa import KamusBahasa
import logging
from typing import Dict, Tuple, Any, List

from app.model.pepper_mode import PepperMode
from app.utils.external_tts import text_to_speech
from app.services.ssh_service import SSHService
from app.controller.ssh_controller import SSHController

class TextController:
    # Error message constants
    INTERNAL_SERVER_ERROR = "Internal server error"
    TEXTS_RETRIEVED_SUCCESSFULLY = "Texts retrieved successfully"
    KAMUS_RETRIEVED_SUCCESSFULLY = "Dictionary texts retrieved successfully"
    KAMUS_ENTRY_ADDED_SUCCESSFULLY = "Dictionary entry added successfully"

    @staticmethod
    def get_kamus_list():
        """
        Get all texts from Kamus_Bahasa table with language-based text selection
        Returns text in Indonesian or English based on Configuration.mobile_app_language
        
        Logic:
        - If mobile_app_language = "indo" -> return text_indo
        - Else -> return text_english
        - Default to "indo" if no Configuration found
        - Sort by created_at DESC
        
        Returns:
            JSON response with status code
            Response format: [
                {
                    "kamus_bahasa_id": 1,
                    "text": "Selamat Pagi", 
                    "is_custom": false,
                    "created_at": "2018-06-13T12:11:13+05:30"
                },
                ...
            ]
        """
        try:
            # Get texts using the new KamusBahasa method
            texts = KamusBahasa.get_text_list_with_language()
            
            # Return the texts directly as array
            return jsonify(texts), 200
            
        except Exception as e:
            logging.error(f"Error getting kamus list: {e}")
            return jsonify({
                "status": 500, 
                "message": TextController.INTERNAL_SERVER_ERROR
            }), 500

    @staticmethod
    def add_kamus_entry(request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Add new dictionary entry with auto-translation.
        For POST /kamus/add endpoint.
        
        Args:
            request_data: Request JSON data containing 'text' field.
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Validate request data
            if not request_data or 'text' not in request_data:
                return {'error': 'Missing required field: text'}, 400
            
            input_text = request_data.get('text', '')
            
            # Call model method for creation with auto-translation
            result = KamusBahasa.create_entry_with_translation(input_text)
            
            # Check if operation was successful
            if not result.get('success', False):
                message = result.get('message', 'Failed to create entry')
                # Use 400 for known errors like duplicates or empty text
                return {'error': message}, 400
            
            # Return successful response
            return {
                'kamus_bahasa_id': result['kamus_bahasa_id'],
                'text': result['text'],
                'is_custom': result['is_custom'],
                'created_at': result['created_at']
            }, 200
            
        except Exception as e:
            logging.error(f"Error in add_kamus_entry controller: {e}")
            return {'error': 'Internal server error'}, 500

    @staticmethod
    def edit_kamus_entry(entry_id: int, request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Edit existing dictionary entry with auto-translation
        For PUT /kamus/edit/{kamus_bahasa_id} endpoint
        
        Args:
            entry_id: Kamus_Bahasa ID to edit
            request_data: Request JSON data containing 'text' field
            
        Returns:
            Tuple of (response_dict, status_code)
            Success response format: {
                'kamus_bahasa_id': int,
                'text': str,
                'is_custom': bool,
                'created_at': str
            }
        """
        try:
            # Validate request data
            if not request_data or 'text' not in request_data:
                return {'error': 'Missing required field: text'}, 400
            
            input_text = request_data.get('text', '')
            
            # Validate entry_id
            if not isinstance(entry_id, int) or entry_id <= 0:
                return {'error': 'Invalid entry ID'}, 400
            
            # Call model method for update with auto-translation
            result = KamusBahasa.update_entry_with_translation(entry_id, input_text)
            
            # Check if operation was successful
            if not result.get('success', False):
                message = result.get('message', 'Failed to update entry')
                
                # Determine appropriate status code based on error
                if 'not found' in message.lower():
                    return {'error': message}, 404
                elif 'already exists' in message.lower():
                    return {'error': message}, 400
                elif 'empty' in message.lower():
                    return {'error': message}, 400
                else:
                    return {'error': message}, 500
            
            # Return successful response (exclude internal fields)
            return {
                'kamus_bahasa_id': result['kamus_bahasa_id'],
                'text': result['text'],
                'is_custom': result['is_custom'],
                'created_at': result['created_at']
            }, 200
            
        except Exception as e:
            print(f"Error in edit_kamus_entry controller: {e}")
            return {'error': 'Internal server error'}, 500

    @staticmethod
    def delete_kamus_entry(entry_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Soft delete a dictionary entry.
        For DELETE /kamus/delete/{kamus_bahasa_id} endpoint.
        
        Args:
            entry_id: Kamus_Bahasa ID to delete
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        try:
            # Validate entry_id format
            if not isinstance(entry_id, int) or entry_id <= 0:
                return {'error': 'Invalid entry ID format'}, 400
            
            # Call model method for soft deletion
            result = KamusBahasa.soft_delete_entry(entry_id)
            
            # If deletion failed (e.g., not found)
            if not result.get('success'):
                message = result.get('message', KamusBahasa.ENTRY_NOT_FOUND)
                return {'message': message}, 404
            
            # Return successful response
            return {
                'status': 200, 
                'deleted_at': result.get('deleted_at')
            }, 200
            
        except Exception as e:
            print(f"Error in delete_kamus_entry controller: {e}")
            return {'error': 'Internal server error'}, 500 
        
    @staticmethod
    def speak_text(kamus_bahasa_id):
        try:
            text_entry = KamusBahasa.get_entry_by_id(kamus_bahasa_id)
            if not text_entry:
                return jsonify({"error": "Text entry not found"}), 404

            config_response, status_code = ConfigController.get_config()

            if status_code != 200:
                return config_response, status_code

            config_data = config_response.get_json()
        
            if not config_data:
                return jsonify({"error": "Configuration not found"}), 500
            
            pepper_mode = PepperMode.get_pepper_mode_by_id(config_data["pepper_mode_id"])

            if not pepper_mode:
                return jsonify({"error": "Pepper mode not found"}), 500
            
            selected_language = pepper_mode["language"]
            if selected_language == "indo":
                voice_type = "id-ID"
                text_type = text_entry['text_indo']
            else:
                voice_type = "en-US"
                text_type = text_entry['text_english']


            selected_voice = pepper_mode["voice"]

            audio_output = text_to_speech(
                text=text_type,
                language_code=voice_type,
                voice_name=selected_voice
            )

            # Call the external TTS service and send file to Pepper
            success = SSHService.send_bytes_to_pepper(
                audio_bytes=audio_output,
                remote_filename=f"tts_{kamus_bahasa_id}.wav", 
                remote_directory="/home/nao/audio/"
            )

            if not success:
                return jsonify({"error": "Failed to send audio to Pepper"}), 500

            play_response, play_status = SSHController.ssh_play_audio(
                filename=f"tts_{kamus_bahasa_id}.wav",
                remote_directory="/home/nao/audio/"
            )
            
            if play_status == 200:
                return jsonify({"message": "Text spoken successfully"}), 200
            else:
                return play_response, play_status

        except Exception as e:
            logging.error(f"Error in speak_text: {e}")
            return jsonify({"error": "Internal server error"}), 500
