from app import app, limiter
from app.controller.auth_controller import AuthController
from app.controller.face_controller import FaceController
from app.controller.user_controller import UserController
from app.controller.forgot_password_controller import ForgotPasswordController
from app.controller.text_controller import TextController
from app.controller.movement_controller import MovementController
from app.controller.config_controller import ConfigController
from app.controller.ssh_controller import SSHController
from app.controller.ai_conversation_controller import AIConversationController
from app.controller.app_redirect_controller import AppRedirectController

from app.utils.jwt_helper import token_required
from flask import jsonify, request, render_template, Response, g
from flasgger import swag_from
import json
import cv2

def generate_frames():
    cap = cv2.VideoCapture(0)  # Kamera hanya aktif di sini

    if not cap.isOpened():
        print("❌ Kamera gagal dibuka")
        return

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    finally:
        # Kamera dimatikan ketika loop selesai
        print("🛑 Kamera dimatikan")
        cap.release()

@app.route("/")
def home():
    menu_cards = [
        {
            "title": "Pengenalan Wajah",
            "image": "ic_face_recognize.png",
            "url": "/face-recognition"
        },
        {
            "title": "Konferensi Video",
            "image": "ic_video_conference.png",
            "url": "/video-conference"
        },
        {
            "title": "Diskusi AI",
            "image": "ic_ai_discussion.png",
            "url": "/conversation-ai"
        },
        {
            "title": "Gerakan Robot",
            "image": "ic_robot_movement.png",
            "url": "/movement-robot"
        }
    ]
    return render_template(
        "index.html", cards=menu_cards
    )
@app.route("/face-recognition")
def face_recognition():
    return render_template(
        "face-recognition.html"
    )
@app.route("/face-recognition/<status>")
def face_recognition_status(status):
    return render_template(
        "face-recognition-status.html", status=status
    )
@app.route("/conversation-ai")
def ai_discussion():
    return render_template(
        "conversation-ai.html"
    )

@app.route("/movement-robot")
def movement_robot():
    return render_template(
        "movement-robot.html"
    )

@app.route("/movement-robot-dance")
def movement_robot_dance():
    return render_template(
        "movement-robot-dance.html"
    )

@app.route("/movement-robot-walk")
def movement_robot_walk():
    return render_template(
        "movement-robot-walk.html"
    )


@app.route("/video_feed")
def video_feed():
     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route("/")
# def home():
#     return "Hello from Flask!"

# @app.route("/pepper-home", methods=['GET'])
# def pepper_home():
#     return render_template('index.html')


@app.route("/authentication/login", methods=['POST'])
# @limiter.limit("5 per minute")  # Max 5 login attempts per minute per IP
@swag_from('../docs/api/login.yml')
def login():
    return AuthController.login()

@app.route("/face/validate_face_image", methods=['POST'])
@token_required
@swag_from('../docs/api/validate_face_image.yml')
def validate_face_image():
    return FaceController.validate_face_image()

@app.route("/user/identities", methods=["GET"])
@token_required
@swag_from('../docs/api/get_identities.yml')
def get_identities():
    return UserController.get_identities()

@app.route("/user/register_identity", methods=['POST'])
@token_required
@swag_from('../docs/api/register_identity.yml')
def add_face():
    return UserController.register_identity()

@app.route("/kamus/list", methods=['GET'])
def get_kamus_list():
    """
    Get all texts from Kamus_Bahasa table with language-based text selection
    Returns text in Indonesian or English based on Configuration.mobile_app_language
    
    Logic:
    - If mobile_app_language = "indo" -> return text_indo
    - Else -> return text_english
    - Default to "indo" if no Configuration found
    - Sort by created_at DESC
    
    Response format:
    [
        {
            "kamus_bahasa_id": 1,
            "text": "Selamat Pagi",
            "is_custom": false,
            "created_at": "2018-06-13T12:11:13+05:30"
        },
        ...
    ]
    """
    return TextController.get_kamus_list()

@app.route("/kamus/add", methods=["POST"])
def add_kamus_entry():
    """Add new dictionary entry with auto-translation"""
    try:
        data = request.get_json()
        response, status_code = TextController.add_kamus_entry(data)
        return jsonify(response), status_code
    except Exception as e:
        print(f"Error in add_kamus_entry route: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/kamus/edit/<int:kamus_bahasa_id>", methods=["PUT"])
def edit_kamus_entry(kamus_bahasa_id):
    """Edit existing dictionary entry with auto-translation"""
    try:
        data = request.get_json()
        response, status_code = TextController.edit_kamus_entry(kamus_bahasa_id, data)
        return jsonify(response), status_code
    except Exception as e:
        print(f"Error in edit_kamus_entry route: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/kamus/delete/<int:kamus_bahasa_id>", methods=["DELETE"])
def delete_kamus_entry(kamus_bahasa_id):
    """Soft delete a dictionary entry by its ID"""
    try:
        response, status_code = TextController.delete_kamus_entry(kamus_bahasa_id)
        return jsonify(response), status_code
    except Exception as e:
        print(f"Error in delete_kamus_entry route: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/user/edit-name/<user_id>", methods=['PUT'])
@token_required
@swag_from('../docs/api/update_user_name.yml')
def update_user_name(user_id):
    """
    Update user name endpoint: PUT /user/edit-name/<user_id>
    Path parameters: user_id
    Request body: {"name": "New Name"}
    """
    return UserController.update_user_name(user_id)

@app.route("/user/delete/<user_id>", methods=['DELETE'])
@token_required
@swag_from('../docs/api/delete_user.yml')
def delete_user(user_id):
    """
    Soft delete user endpoint: DELETE /user/delete/<user_id>
    Path parameters: user_id
    """
    return UserController.delete_user(user_id)

@app.route("/<user_id>", methods=['GET'])
@token_required
@swag_from('../docs/api/get_user_by_id.yml')
def get_user_by_id(user_id):
    """
    Get user by ID endpoint: GET /user/<user_id>
    Path parameters: user_id
    """
    return UserController.get_user_by_id(user_id)

@app.route("/user/recognize", methods=['POST'])
@swag_from('../docs/api/recognize_user.yml')
def recognize_user():
    """
    Recognize user endpoint: POST /user/recognize
    Request body: {"image": "base64_encoded_image"}
    """
    return FaceController.recognize_user_face()

@app.route("/authentication/forgot-password", methods=['POST'])
@limiter.limit("3 per hour")  # Max 3 forgot password requests per hour per IP
@swag_from('../docs/api/forgot_password.yml')
def forgot_password():
    """
    Forgot password endpoint: POST /authentication/forgot-password
    Request body: {"email": "admin@example.com"}
    """
    return ForgotPasswordController.forgot_password()

@app.route("/change-password", methods=['POST'])
@swag_from('../docs/api/change_password.yml')
def change_password():
    """
    Change password endpoint: POST /change-password
    Request body: {"token": "abc123", "new_password": "newpass123"}
    """
    return ForgotPasswordController.reset_password()

@app.route("/api/renew-password", methods=['POST'])
@swag_from('../docs/api/renew_password.yml')
def renew_password():
    """
    Renew password endpoint: POST /api/renew-password
    Request body: {"token": "abc123", "new_password": "newpass123"}
    """
    return ForgotPasswordController.reset_password()

@app.route("/api/validate-token", methods=['POST'])
@swag_from('../docs/api/validate_token.yml')
def validate_token():
    """
    Validate reset token endpoint: POST /api/validate-token
    Request body: {"token": "abc123"}
    """
    return ForgotPasswordController.validate_token()

# Admin maintenance endpoints
@app.route("/api/admin/cleanup-tokens", methods=['POST'])
@token_required
@swag_from('../docs/api/cleanup_expired_tokens.yml')
def cleanup_expired_tokens():
    """
    Cleanup expired tokens endpoint: POST /api/admin/cleanup-tokens
    Protected endpoint for admin maintenance
    """
    return ForgotPasswordController.cleanup_expired_tokens()

@app.route("/api/admin/token-stats", methods=['GET'])
@token_required
@swag_from('../docs/api/get_token_stats.yml')
def get_token_stats():
    """
    Get token statistics endpoint: GET /api/admin/token-stats
    Protected endpoint for monitoring
    """
    return ForgotPasswordController.get_token_stats()

@app.route("/app-redirect/reset-password", methods=['GET'])
def app_redirect_reset_password():
    """
    App redirect endpoint for reset password: GET /app-redirect/reset-password?token=abc123
    This endpoint handles universal links that work in email clients
    """
    return AppRedirectController.redirect_to_app()

@app.route('/capture_face/recognize', methods=['GET'])
# @token_required
def capture_face_recognize():
    return SSHController.run_and_parsing_face_recognition_script("/home/nao/pepper_client/face_reco_pepper_new4.py")

# @app.route('/stream_camera', methods=['GET'])
# def stream_camera():
#     return SSHController.run_script_with_env("/home/nao/stream.py")

# Example protected route
@app.route("/api/protected", methods=['GET'])
@token_required
@swag_from('../docs/api/protected.yml')
def protected_route():
    """Example protected route"""
    return jsonify({
        'message': 'This is a protected route',
        'user': g.current_user
    }), 200

# Movement Sequences endpoints
@app.route("/<feature>/movement-sequences-list", methods=['GET'])
def get_movement_sequences_list(feature):
    """
    Get all movement sequences with commands and additional actions details
    
    Returns:
        List of movement sequences with hierarchical structure
    """
    return MovementController.get_movement_sequences_list()

@app.route("/<feature>/movement-sequences-list/<movement_sequence_id>", methods=['GET'])
def get_movement_sequence_by_id(feature, movement_sequence_id):
    """
    Get specific movement sequence with commands and additional actions details by ID
    
    Args:
        feature: Feature parameter from URL
        movement_sequence_id: Movement sequence ID from URL
        
    Returns:
        Single movement sequence object with hierarchical structure
    """
    return MovementController.get_movement_sequence_by_id(movement_sequence_id)

@app.route("/<feature>/movement-sequences-list/tablet/<movement_sequence_id>", methods=['GET'])
def get_movement_sequence_for_tablet(feature, movement_sequence_id):
    """
    Get movement sequence data for tablet interface
    
    Args:
        feature: Feature parameter from URL
        movement_sequence_id: Movement sequence ID from URL
        
    Returns:
        Movement sequence data formatted for tablet: {id, name, description, route_map_image_path}
    """
    return MovementController.get_movement_sequence_for_tablet(movement_sequence_id)

# Config endpoints
@app.route("/<feature>/config", methods=['GET'])
@token_required
def get_config(feature):
    """
    Get pepper mode configuration with is_used flag based on current admin's configuration
    
    Args:
        feature: Feature parameter from URL
        
    Returns:
        List of pepper modes with is_used flag indicating which one is currently used by admin
        
    Response format:
    [
        {
            "pepper_mode_id": 1,
            "language": "indo",
            "voice": "pepper_mode_1",
            "created_at": "2025-07-02 05:08:39",
            "is_used": true
        },
        ...
    ]
    """
    return ConfigController.get_config()

@app.route("/<feature>/config", methods=['POST'])
@token_required
def post_config(feature):
    """
    Update pepper mode configuration for current admin
    
    Args:
        feature: Feature parameter from URL
        
    Request body:
        {
            "new_pepper_mode_id": "1"
        }
        
    Returns:
        {
            "status": 200,
            "message": "Configuration changed successfully"
        }
    """
    return ConfigController.update_config()

@app.route("/tts/speak/<kamus_bahasa_id>", methods=['POST'])
@token_required
def speak_text(kamus_bahasa_id):
    """
    Speak text using TTS service based on kamus_bahasa_id
    """
    return TextController.speak_text(kamus_bahasa_id)

@app.route("/ai_conversation/record", methods=['POST'])
# @token_required
def record_ai_conversation():
    """
    Record AI conversation endpoint: POST /ai_conversation/record
    Request body: {"conversation": "AI conversation text"}
    """
    return AIConversationController.record_ai_conversation()

@app.route("/ai_conversation/stop-record", methods=['POST'])
# @token_required
def stop_record_ai_conversation():
    """
    Stop recording AI conversation endpoint: POST /ai_conversation/stop-record
    Request body: {"session_id": "abc123"}
    """
    return AIConversationController.stop_ai_conversation()

@app.route("/ai_conversation/reset", methods=['POST'])
# @token_required
def reset_ai_conversation():
    """
    Reset AI conversation endpoint: POST /ai_conversation/reset
    """
    return AIConversationController.reset_ai_conversation()

@app.route("/ai_conversation/play-audio-conversation", methods=['POST'])
# @token_required
def play_audio_conversation():
    """
    Play audio conversation endpoint: POST /ai_conversation/play-audio-conversation
    """
    return AIConversationController.play_audio_conversation()

@app.route("/ai_conversation/stop-audio-conversation", methods=['POST'])
# @token_required
def stop_audio_conversation():
    return AIConversationController.stop_audio_conversation()

@app.route("/movement/movement-sequences-list/add", methods=['POST'])
@token_required
def add_movement_sequence():
    """
    Add new movement sequence endpoint: POST /movement/movement-sequences-list/add
    
    Request body:
    {
        "name": "string",
        "description": "string (optional)",
        "commands": [
            {
                "type": "enum (FORWARD, BACKWARD, ROTATE_LEFT, ROTATE_RIGHT)",
                "value": "float",
                "step_order": "integer",
                "additional_actions": [
                    {
                        "action_name": "string",
                        "additional_step_order": "integer"
                    }
                ]
            }
        ]
    }
    """
    return MovementController.add_movement_sequence()

@app.route("/movement/movement-sequences-list/<movement_sequence_id>/delete/<movement_command_id>", methods=['POST'])
@token_required
def delete_movement_command(movement_sequence_id, movement_command_id):
    """
    Delete movement command endpoint: POST /movement/movement-sequences-list/<movement_sequence_id>/delete/<movement_command_id>
    
    Flow:
    1. Get target Movement_Command by movement_command_id
    2. Get all Movement_Command objects for the movement_sequence_id
    3. Reorder step_order: decrease by 1 for commands with step_order > target.step_order
    4. Delete target command (cascade delete Movement_Additional_Action)
    
    Response:
    {
        "status": 200,
        "message": "Deletion success"
    }
    """
    return MovementController.delete_movement_command(movement_sequence_id, movement_command_id)

@app.route("/movement/movement-sequences-list/swap_order", methods=['POST'])
@token_required
def swap_movement_command_order():
    """
    Swap movement command order endpoint: POST /movement/movement-sequences-list/swap_order
    
    Flow:
    1. Get Movement_Command by movement_command_id_one
    2. Get Movement_Command by movement_command_id_two
    3. Swap step_order between the two commands
    
    Request body:
    {
        "movement_command_id_one": "uuid",
        "movement_command_id_two": "uuid"
    }
    
    Response:
    {
        "status": 200,
        "message": "Swap success"
    }
    """
    return MovementController.swap_movement_command_order()

@app.route("/<feature>/movement-sequences-list/<movement_sequence_id>/delete", methods=['POST'])
@token_required
def delete_movement_sequence(feature, movement_sequence_id):
    """
    Delete movement sequence endpoint: POST /<feature>/movement-sequences-list/<movement_sequence_id>/delete
    
    Flow:
    1. Get object Movement_Sequence where Movement_Sequence.movement_sequence_id == <movement_sequence_id>
    2. Delete object cascade all related Movement_Command objects and Movement_Additional_Action objects
    
    Args:
        feature: Feature parameter from URL
        movement_sequence_id: Movement sequence ID from URL parameter
        
    Response:
    {
        "status": 200,
        "message": "Deletion success"
    }
    """
    return MovementController.delete_movement_sequence(movement_sequence_id)

@app.route("/movement/movement-sequences-list/update/<movement_sequence_id>", methods=['PUT'])
@token_required
def update_movement_sequence(movement_sequence_id):
    """
    Update movement sequence endpoint: PUT /movement/movement-sequences-list/update/<movement_sequence_id>
    
    Flow (Delete + Create with Same ID approach):
    1. Validate movement_sequence_id exists
    2. Delete existing Movement_Sequence (cascade delete commands & actions)
    3. Create new Movement_Sequence with same ID + new data from request
    4. Create commands & additional_actions from request body
    
    Request body:
    {
        "name": "string",
        "description": "string (optional)",
        "commands": [
            {
                "type": "FORWARD|BACKWARD|ROTATE_LEFT|ROTATE_RIGHT",
                "value": 0.0,
                "step_order": 1,
                "additional_actions": [
                    {
                        "action_name": "string", 
                        "additional_step_order": 1
                    }
                ]
            }
        ]
    }
    
    Response:
    {
        "message": "Update success",
        "id": 12,
        "name": "Updated name",
        "description": "Updated description",
        "created_at": "2025-01-XX...",
        "movement_sequences": [/* command details */]
    }
    """
    return MovementController.update_movement_sequence(movement_sequence_id)