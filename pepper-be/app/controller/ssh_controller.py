import logging
from flask import jsonify, request
import re
import json
from app.services.ssh_service import SSHService
from app.model.face_data import FaceData
import ast

class SSHController:
    @staticmethod
    def run_script_with_env(script_path):
        command = f'export PYTHONPATH=/opt/aldebaran/lib/python2.7/site-packages:$PYTHONPATH && cd /home/nao && python {script_path}'
        output, error = SSHService.send_ssh_command(command)
        return jsonify({
            "status": "sent",
            "script": script_path,
            "command": command,
            "output": output,
            "error": error
        })
    
    def _parse_server_response(output):
        """
        Parse the server response from script output to extract the full response dict.
        """
        try:
            # Cari pola response yang mengandung dict Python
            pattern = r"\[INFO\] Server response:', ({.*?})\)"
            match = re.search(pattern, output)

            if match:
                response_str = match.group(1)
                # Gunakan ast.literal_eval untuk parsing dictionary Python
                response_dict = ast.literal_eval(response_str)
                print(f"Parsed server response: {response_dict}")
                return response_dict
            return None
        except Exception as e:
            print(f"Error parsing server response: {e}")
            return None


    @staticmethod
    def run_and_parsing_face_recognition_script(script_path):
        """
        Run the face recognition script and return the output with parsed status.
        """
        # Use existing run_script_with_env function
        script_response = SSHController.run_script_with_env(script_path)
        script_data = script_response.get_json()
        
        output = script_data.get('output', '')
        error = script_data.get('error', '')

        print("output:", output)
        print("error:", error)
        
        # Parse the server response from output to get full response dict
        parsed_response = SSHController._parse_server_response(output)
        
        if parsed_response and parsed_response.get('status') == 200:
            response = jsonify({
                "status": "success",
                "status_code": parsed_response.get('status'),
                "message": "Success",
                "name": parsed_response.get('name'),
                "face_image_base64": FaceData.get_face_image_base64_by_name(parsed_response.get('name')),
                "output": output
            })
            # response_data = response.get_json()
            # print(f"response: {response_data}")
            return response, 200
        elif parsed_response and parsed_response.get('status') == 400:
            response = jsonify({
                "status": "client_error", 
                "status_code": parsed_response.get('status'),
                "message": "Client error",
                "output": output
            })
            return response, 400
        elif parsed_response and parsed_response.get('status') == 500:
            response = jsonify({
                "status": "server_error",
                "status_code": parsed_response.get('status'), 
                "message": "Server error",
                "output": output
            })
            return response, 500
        
        # Default response if parsing fails or no status found
        response = jsonify({
            "status": "unknown",
            "message": "Could not parse server response",
            "output": output,
            "error": error
        })
        return response, 500

    @staticmethod
    def ssh_play_audio(filename, remote_directory="/home/nao/audio/"):
        try:
            remote_path = f"{remote_directory}{filename}"
            print(f"Remote path: {remote_path}")

            command = f"qicli call ALAudioPlayer.playFile \"{remote_path}\""
            
            success = SSHService.send_ssh_command(command)
            print(f"Command executed: {command}")
            print(f"Success: {success}")

            if success:
                return jsonify({"message": "Audio played successfully"}), 200
            else:
                return jsonify({"error": "Failed to play audio on Pepper"}), 500

        except Exception as e:
            logging.error(f"Error in ssh_play_audio: {e}")
            return jsonify({"error": "Internal server error"}), 500
        
    @staticmethod
    def ssh_stop_audio():
        try:
            command = "qicli call ALAudioPlayer.stopAll"
            
            success = SSHService.send_ssh_command(command)
            print(f"Command executed: {command}")
            print(f"Success: {success}")

            if success:
                return jsonify({"message": "Audio stopped successfully"}), 200
            else:
                return jsonify({"error": "Failed to stop audio on Pepper"}), 500

        except Exception as e:
            logging.error(f"Error in ssh_stop_audio: {e}")
            return jsonify({"error": "Internal server error"}), 500

