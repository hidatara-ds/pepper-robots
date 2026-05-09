# Pepper Robot Management System

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)

A comprehensive, production-ready management system for Pepper humanoid robots, featuring advanced capabilities in AI integration, face recognition, natural language processing, and robotic control.

**Author**: Gilang Hidayatullah

---

## Project Objectives

- **Full-Stack Development**: Complete backend API with modern web interfaces
- **AI/ML Integration**: Advanced face recognition and conversational AI capabilities
- **Cloud-Native Architecture**: Integration with Google Cloud Platform services
- **Robotic Control Systems**: Comprehensive movement and interaction management
- **Production-Ready Code**: Well-structured, documented, and tested codebase

---

## System Architecture

### 1. Backend Management System (ackend/)
A Flask-based RESTful API backend providing comprehensive robot management capabilities:
- User authentication and authorization
- Face recognition and identity management
- Robot movement and sequence control
- AI conversation integration
- SSH-based robot communication
- Multi-language support (Indonesian/English)
- Web-based administration interface

**Key Technologies:** Python 3.11, Flask, SQLAlchemy, JWT, Google Cloud Storage

### 2. AI Conversation Service (i-chat/)
An intelligent voice-based conversation system:
- Speech-to-Text using Google Cloud Speech-to-Text API
- Natural language processing with Google Vertex AI (Gemini)
- Text-to-Speech with Google Cloud TTS
- Session management and conversation history
- Docker containerization for cloud deployment

**Key Technologies:** Flask, Vertex AI (Gemini 2.0 Flash), Google Cloud STT/TTS, Docker

### 3. Face Recognition Service (ace-recognition/)
Advanced face recognition system with cloud storage integration:
- Real-time face detection and recognition
- DeepFace-based facial analysis
- Google Cloud Storage as distributed database
- Automatic synchronization and caching
- RESTful API for robot integration

**Key Technologies:** Flask, DeepFace, OpenCV, Google Cloud Storage, VGG-Face

---

## Key Features

- **Robot Control**: Movement sequence management, dance/walk patterns, SSH command execution
- **Face Recognition**: Real-time detection, multi-person recognition, cloud-based database
- **AI Conversation**: Natural language understanding, voice I/O, multi-turn dialogue
- **Security**: JWT authentication, password reset, secure credential management
- **Web Interface**: Responsive admin dashboard, real-time monitoring, multi-language UI

---

## Technical Stack

| Category | Technologies |
|----------|-------------|
| Backend | Python 3.11, Flask, SQLAlchemy, JWT, OpenCV, DeepFace |
| Cloud | Google Cloud Storage, Speech-to-Text, Text-to-Speech, Vertex AI |
| Frontend | HTML5/CSS3, JavaScript/jQuery, Bootstrap |
| DevOps | Docker, Git, Virtual Environments |

---

## Project Structure

`
pepper-robots/
├── backend/                       # Main backend management system
│   ├── app/
│   │   ├── controller/           # API controllers
│   │   ├── model/                # Database models
│   │   ├── services/             # Business logic services
│   │   ├── templates/            # Web UI templates
│   │   ├── static/               # CSS, JS, images
│   │   └── utils/                # Utility functions
│   ├── tests/                    # Unit and integration tests
│   └── docs/                     # API documentation
├── ai-chat/                      # AI conversation service
│   ├── app.py                    # Main Flask application
│   ├── Dockerfile                # Container configuration
│   └── requirements.txt          # Python dependencies
└── face-recognition/             # Face recognition service
    ├── app.py                    # Face recognition API
    ├── gcs_handler.py            # Cloud storage integration
    └── pepper_client.py          # Robot client library
`

---

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Google Cloud Platform account with appropriate APIs enabled
- Access to Pepper robot (for full functionality testing)

### Quick Start

1. **Clone the repository**
   `ash
   git clone https://github.com/hidatara-ds/pepper-robots.git
   cd pepper-robots
   `

2. **Set up backend system**
   `ash
   cd backend
   python -m venv venv
   # Windows:
   venv\\Scripts\\activate
   # Linux/Mac:
   source venv/bin/activate
   pip install -r requirements.txt
   `

3. **Configure environment variables**
   - Copy .env.example to .env and fill in your credentials
   - Configure Google Cloud credentials (see individual README files)

4. **Run the application**
   `ash
   python run.py
   `

For detailed setup instructions for each component, refer to the individual README files in each subdirectory.

---

## License

Licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

Copyright 2026 Gilang Hidayatullah

---

## Citation

If you reference this work, please cite:

`ibtex
@software{hidayatullah2026pepper,
  author = {Hidayatullah, Gilang},
  title = {Pepper Robot Management System: A Comprehensive AI-Integrated Robotic Control Platform},
  year = {2026},
  url = {https://github.com/hidatara-ds/pepper-robots}
}
`
