# 🤖 Pepper Robot Management System

> **Note**: This project was originally developed as part of an Apple Developer Academy application portfolio and represents significant personal effort. While it's open source under MIT License, please provide proper attribution when using this code.

---

## 📋 Project Overview

This project demonstrates a comprehensive, production-ready management system for Pepper humanoid robots, showcasing advanced capabilities in AI integration, face recognition, natural language processing, and robotic control.

---

## 🎯 Project Objectives

This project was created to demonstrate:

- **Full-Stack Development Expertise**: Complete backend API with modern web interfaces
- **AI/ML Integration**: Advanced face recognition and conversational AI capabilities
- **Cloud-Native Architecture**: Integration with Google Cloud Platform services
- **Robotic Control Systems**: Comprehensive movement and interaction management
- **Production-Ready Code**: Well-structured, documented, and tested codebase

---

## 🏗️ System Architecture

The project consists of three main components, each demonstrating different aspects of modern software development:

### 1. **Pepper Backend Management System** (`pepper-be/`)
A Flask-based RESTful API backend providing comprehensive robot management capabilities:
- User authentication and authorization
- Face recognition and identity management
- Robot movement and sequence control
- AI conversation integration
- SSH-based robot communication
- Multi-language support (Indonesian/English)
- Web-based administration interface

**Key Technologies:**
- Python 3.11.1, Flask
- SQLite database with SQLAlchemy ORM
- JWT authentication
- Google Cloud Storage integration
- RESTful API design

### 2. **AI Conversation Service** (`pepper-ai-discussion/`)
An intelligent voice-based conversation system:
- Speech-to-Text using Google Cloud Speech-to-Text API
- Natural language processing with Google Vertex AI (Gemini)
- Text-to-Speech with Google Cloud TTS
- Session management and conversation history
- Docker containerization for cloud deployment

**Key Technologies:**
- Flask REST API
- Google Vertex AI (Gemini 2.0 Flash)
- Google Cloud Speech-to-Text & Text-to-Speech
- Docker & Cloud Run deployment ready

### 3. **Face Recognition Application** (`final test face reco app/`)
Advanced face recognition system with cloud storage integration:
- Real-time face detection and recognition
- DeepFace-based facial analysis
- Google Cloud Storage as distributed database
- Automatic synchronization and caching
- RESTful API for robot integration

**Key Technologies:**
- Flask API
- DeepFace library
- OpenCV for image processing
- Google Cloud Storage
- VGGFace model integration

---

## ✨ Key Features

### 🤖 Robot Control
- Movement sequence management
- Dance and walk pattern control
- Real-time robot state monitoring
- SSH-based command execution

### 👤 Face Recognition
- Real-time face detection and identification
- Multi-person recognition
- Cloud-based face database
- Automatic model synchronization

### 💬 AI Conversation
- Natural language understanding
- Context-aware conversations
- Voice input/output support
- Multi-turn dialogue management

### 🔐 Security & Authentication
- JWT-based authentication
- Password reset functionality
- Secure credential management
- Role-based access control

### 🌐 Web Interface
- Responsive admin dashboard
- Real-time status monitoring
- Interactive robot control panels
- Multi-language UI support

---

## 🛠️ Technical Stack

### Backend
- **Python 3.11.1** - Core programming language
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database management
- **JWT** - Authentication tokens
- **OpenCV** - Computer vision
- **DeepFace** - Face recognition

### Cloud Services
- **Google Cloud Storage** - Distributed file storage
- **Google Cloud Speech-to-Text** - Voice recognition
- **Google Cloud Text-to-Speech** - Voice synthesis
- **Google Vertex AI (Gemini)** - Natural language processing

### Frontend
- **HTML5/CSS3** - Modern web standards
- **JavaScript/jQuery** - Interactive UI
- **Bootstrap** - Responsive design framework

### DevOps
- **Docker** - Containerization
- **Git** - Version control
- **Virtual Environments** - Dependency isolation

---

## 📁 Project Structure

```
pepper-robots/
├── pepper-be/                    # Main backend management system
│   ├── app/
│   │   ├── controller/          # API controllers
│   │   ├── model/               # Database models
│   │   ├── services/            # Business logic services
│   │   ├── templates/           # Web UI templates
│   │   ├── static/              # CSS, JS, images
│   │   └── utils/               # Utility functions
│   ├── tests/                   # Unit and integration tests
│   └── docs/                    # API documentation
│
├── pepper-ai-discussion/         # AI conversation service
│   ├── app.py                   # Main Flask application
│   ├── Dockerfile               # Container configuration
│   └── requirements.txt         # Python dependencies
│
└── final test face reco app/    # Face recognition service
    ├── app.py                   # Face recognition API
    ├── gcs_handler.py           # Cloud storage integration
    └── pepper_client.py         # Robot client library
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11.1 or higher
- Google Cloud Platform account with appropriate APIs enabled
- Access to Pepper robot (for full functionality testing)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pepper-robots
   ```

2. **Set up backend system**
   ```bash
   cd pepper-be
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Set up `.env` file with database and API credentials
   - Configure Google Cloud credentials

4. **Run the application**
   ```bash
   python run.py
   ```

For detailed setup instructions for each component, please refer to the individual README files in each subdirectory.

---

## 📊 Project Highlights

### Code Quality
- ✅ Modular architecture with separation of concerns
- ✅ Comprehensive error handling
- ✅ RESTful API design principles
- ✅ Database normalization and optimization
- ✅ Security best practices implementation

### Innovation
- 🔬 Integration of multiple AI services
- 🔬 Cloud-native architecture
- 🔬 Real-time robot-human interaction
- 🔬 Scalable microservices design

### Documentation
- 📚 Inline code documentation
- 📚 API endpoint documentation
- 📚 Setup and deployment guides
- 📚 Architecture diagrams and explanations

---

## 🎓 Learning Outcomes Demonstrated

This project showcases proficiency in:

1. **Software Engineering**: Clean code, design patterns, architecture
2. **AI/ML Integration**: Face recognition, NLP, speech processing
3. **Cloud Computing**: GCP services, distributed systems
4. **Full-Stack Development**: Backend APIs, frontend interfaces
5. **DevOps**: Containerization, deployment automation
6. **Robotics**: Robot control systems, sensor integration

---

## 📝 Notes for Reviewers

This project was specifically designed and developed as a comprehensive portfolio piece for Apple Developer Academy submission. All code, documentation, and architecture decisions were made with the intention of demonstrating:

- **Technical Competency**: Advanced programming and system design skills
- **Best Practices**: Industry-standard development methodologies
- **Innovation**: Creative integration of modern technologies
- **Completeness**: Full-stack, production-ready system

The codebase is production-ready and demonstrates real-world application development capabilities suitable for enterprise-level projects.

---

## 📄 License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 🙏 Attribution

If you use this code in your project, please provide attribution by mentioning the original author and linking back to this repository. This project represents significant personal effort and was developed as part of an Apple Developer Academy application portfolio.

While this code is open source and free to use, proper attribution is requested to acknowledge the work and effort invested in creating this comprehensive system.

---

## 👤 Author

Developed as a portfolio project for Apple Developer Academy submission, showcasing comprehensive software development capabilities in robotics, AI, and cloud computing.

---

**Project Status**: ✅ Complete and Ready for Review

**Submission Date**: 2025

**Institution**: Apple Developer Academy
