from flask import jsonify
import json
import app.controller.ssh_controller as SSHController

class AIConversationController:
    # Global session storage
    session_data_map = {}

    @staticmethod
    def record_ai_conversation():
        # Format path untuk dipanggil via SSHController
        script_path = f'audiot.py start'

        try:
            return SSHController.SSHController.run_script_with_env(script_path)
        except Exception as e:
            return jsonify({
                "status": 500,
                "message": str(e)
            })
        
    @staticmethod
    def stop_ai_conversation():
        script_path = 'audiot.py stop'

        try:
            response = SSHController.SSHController.run_script_with_env(script_path)

            # Ambil data dict dari Flask Response
            result = response.get_json()

            output = result["output"].lower()

            # Deteksi error dari hasil output
            if "fatal" in output or "error" in output or "http error" in output or "400 client error" in output:
                return jsonify({
                    "status": 500,
                    "message": "Internal server error: AI processing failed.",
                    "details": result
                }), 500

            return jsonify({
                "status": 200,
                "message": "AI conversation stopped successfully.",
                "details": result
            }), 200

        except Exception as e:
            return jsonify({
                "status": 500,
                "message": f"Internal server error: {str(e)}"
            }), 500

        
            
    @staticmethod
    def reset_ai_conversation():
        """
        Reset the AI conversation session.
        """
        
        script_path = f'audiot.py reset'
        try:
            response = SSHController.SSHController.run_script_with_env(script_path)
            return response
        except Exception as e:
            return jsonify({
                "status": 500,
                "message": str(e)
            })
        
    @staticmethod
    def play_audio_conversation():
        """
        Play the recorded audio conversation.
        """
        try:
            # Call the SSHController to play the audio
            response = SSHController.SSHController.ssh_play_audio(
                filename="response.wav",
                remote_directory="/tmp/"
                )
            return response
        except Exception as e:
            return jsonify({
                "status": 500,
                "message": str(e)
            })
        
    @staticmethod
    def stop_audio_conversation():
        try: 
            response = SSHController.SSHController.ssh_stop_audio()
            return response
        except Exception as e:
            return jsonify({
                "status": 500,
                "message": str(e)
            })

        