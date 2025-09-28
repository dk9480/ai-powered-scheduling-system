# 🤖 AI-Powered Appointment Scheduler

A sophisticated multi-service backend system that intelligently processes natural language and image-based appointment requests, converting them into structured scheduling data through OCR, NLP, and normalization pipelines.

## 🚀 Features

- **Multi-modal Input Processing** - Handle both text inputs and image uploads
- **Advanced OCR Processing** - Extract and clean text from images using EasyOCR with typo correction
- **Intelligent Entity Extraction** - Detect date phrases, time expressions, and medical departments using regex patterns
- **Dynamic Normalization** - Convert relative dates to actual calendar dates and times to 24-hour format
- **Confidence Scoring** - Weighted confidence metrics across OCR, entity extraction, and normalization steps
- **Guardrail System** - Intelligent handling of ambiguous or incomplete inputs
- **File Upload Handling** - Secure image processing with automatic cleanup
- **RESTful API** - Well-structured JSON responses with detailed processing metadata

## 🏗️ System Architecture

### **Multi-Service Architecture**
┌─────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Client │ │ Node.js │ │ Python Flask │
│ (Postman/ │───▶│ Express.js │───▶│ Microservices │
│ Frontend) │ │ API Gateway │ │ │
└─────────────────┘ └──────────────────┘ └──────────────────┘
│ │ │
│ HTTP Requests │ Axios HTTP Calls │ OCR & NLP
│ JSON/Form-Data │ Service Communication │ Processing
│ │ │
┌─────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Structured │ │ Processing │ │ EasyOCR & │
│ JSON Response │◀───│ Pipeline │◀───│ Regex Engine │
└─────────────────┘ └──────────────────┘ └──────────────────┘



### **Processing Pipeline**
1. **Input Reception** - Receive text or image via REST API endpoints
2. **OCR Service** - Extract text from images using EasyOCR with automatic typo correction
3. **Entity Extraction Service** - Identify date phrases, time expressions, and departments using advanced regex patterns
4. **Normalization Service** - Convert relative dates to ISO dates and times to 24-hour format
5. **Validation & Guardrails** - Check for ambiguous inputs and request clarification
6. **Response Assembly** - Combine processed data with confidence scores and metadata

## 🛠️ Technology Stack

### **Backend Layer (Node.js)**
- **Runtime**: Node.js with Express.js framework
- **File Handling**: Multer for secure file uploads
- **HTTP Client**: Axios for inter-service communication
- **CORS**: Cross-origin resource sharing enabled
- **File System**: Native fs module for directory management

### **AI/ML Services (Python)**
- **Web Framework**: Flask for microservice APIs
- **OCR Engine**: EasyOCR with pre-trained English models
- **Image Processing**: PIL/Pillow for image handling
- **HTTP Requests**: Requests library for image downloading
- **Pattern Matching**: Advanced regex for entity extraction
- **Date/Time**: datetime and timedelta for date calculations

### **Development & Testing**
- **API Testing**: Postman collection with test scripts
- **Error Handling**: Comprehensive try-catch with detailed logging
- **Validation**: Input validation and guardrail mechanisms

## 📦 Installation & Setup

### **Prerequisites**
- Node.js (v14.0 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)
- Git

### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/ai-appointment-scheduler.git
cd ai-appointment-scheduler


2. Backend Setup (Node.js)
# Navigate to backend directory
cd backend

# Install dependencies
npm install express cors multer axios

# Create uploads directory
mkdir -p uploads

# Start the server (runs on port 5000)
node server.js



3. Python Services Setup
OCR Service (Port 5001)
cd python-services/ocr-services

# Install Python dependencies
pip install flask flask-cors easyocr pillow requests numpy torch torchvision opencv-python

# Start OCR service
python app.py


Entity Service (Port 5002)
cd python-services/entity-services

# Install Python dependencies
pip install flask flask-cors

# Start Entity service
python app.py


📚 API Documentation
Base URLs
Main API: http://localhost:5000

OCR Service: http://localhost:5001

Entity Service: http://localhost:5002


Health Check Endpoints
GET /health

Response:
{
  "status": "OK",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "Appointment Scheduler API"
}


1. Process Appointment Request
POST /api/appointments/process
Content-Type: application/json

Request Body:
{
  "text": "Book dentist next Friday at 3pm",
  "imageUrl": "https://example.com/image.jpg"
}

Success Response:
{
  "appointment": {
    "department": "Dentistry",
    "date": "2024-01-19",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  },
  "status": "ok",
  "confidence": 0.85,
  "extracted_text": "Book dentist next Friday at 3pm",
  "processing_steps": {
    "ocr_confidence": 1.0,
    "entity_confidence": 0.85,
    "normalization_confidence": 0.90
  }
}



2. Upload and Process Image
POST /api/appointments/upload
Content-Type: multipart/form-data

Form Data:

image: File upload (JPEG, PNG, GIF, BMP - max 5MB)


3. Processing History
GET /api/appointments/history

🔬 API Testing Guide
Postman Collection Setup
Environment Variables
{
  "base_url": "http://localhost:5000",
  "ocr_url": "http://localhost:5001", 
  "entity_url": "http://localhost:5002"
}


Essential Test Requests
1. Health Check
GET {{base_url}}/health

2. Process Text Appointment
POST {{base_url}}/api/appointments/process
Content-Type: application/json

{
  "text": "Book dentist next Friday at 6pm"
}

3. Process Image URL
POST {{base_url}}/api/appointments/process
Content-Type: application/json

{
  "imageUrl": "https://example.com/appointment-note.jpg"
}

4. Upload Image File
POST {{base_url}}/api/appointments/upload
Content-Type: multipart/form-data

Form Data:
- Key: image, Type: File

<img width="969" height="405" alt="image" src="https://github.com/user-attachments/assets/374a4485-9cf8-47c5-b001-fc9b8d551ed3" />
<img width="922" height="326" alt="image" src="https://github.com/user-attachments/assets/b91dd14d-d0b5-4fad-8bed-a0e140131e6b" />
<img width="965" height="476" alt="image" src="https://github.com/user-attachments/assets/369a9abe-1272-4530-9f0b-479e9a9353fb" />


🔧 Technical Implementation Details
OCR Service Features
EasyOCR Integration: Uses pre-trained English models for text extraction

Typo Correction: Automatic correction of common OCR errors (nxt→next, Zpm→3pm)

Text Cleaning: Removes extra whitespace and normalizes text

Confidence Scoring: Average confidence across all detected text regions



Entity Extraction Patterns
# Date patterns
date_patterns = [
    r'(next|this|coming)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
    r'\b(tomorrow|today|yesterday)\b',
    r'\b(next\s+week)\b',
    r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
]

# Time patterns  
time_patterns = [
    r'\b(\d{1,2}:\d{2}\s*(am|pm)?)\b',
    r'\b(\d{1,2}\s*(am|pm))\b',
    r'\b(\d{1,2})\b(?![:\d])'
]


Normalization Logic
Date Calculation: Dynamic calculation based on current date

Time Conversion: 12-hour to 24-hour format with AM/PM handling

Timezone Support: Fixed to Asia/Kolkata timezone

Fallback Mechanisms: Default values when parsing fails



📊 Expected Output Examples
Successful Processing
Input: "Book dentist next Friday at 6pm"
{
  "appointment": {
    "department": "Dentistry",
    "date": "2024-01-19",
    "time": "18:00",
    "tz": "Asia/Kolkata"
  },
  "status": "ok",
  "confidence": 0.88,
  "extracted_text": "Book dentist next Friday at 6pm",
  "processing_steps": {
    "ocr_confidence": 1.0,
    "entity_confidence": 0.85,
    "normalization_confidence": 0.90
  }
}


📁 Project Structure
ai-appointment-scheduler/
├── 📁 backend/                          # Node.js Express Server
│   ├── 📁 routes/
│   │   └── appointments.js              # API route handlers
│   ├── 📁 services/
│   │   └── externalServices.js          # Python service communication
│   ├── 📁 uploads/                      # Temporary file storage
│   ├── server.js                        # Main Express server
│   └── package.json                     # Node.js dependencies
├── 📁 python-services/                  # Python Microservices
│   ├── 📁 ocr-services/
│   │   ├── app.py                       # Flask OCR service (Port 5001)
│   │   └── requirements.txt             # Python dependencies
│   └── 📁 entity-services/
│       ├── app.py                       # Flask entity service (Port 5002)
│       └── requirements.txt             # Python dependencies
└── README.md                            # This documentation



🎯 Quick Start
1. Start all services in separate terminals:
# Terminal 1: OCR Service
cd python-services/ocr-services && python app.py

# Terminal 2: Entity Service  
cd python-services/entity-services && python app.py

# Terminal 3: Main Server
cd backend && node server.js


2. Test basic functionality:
curl -X POST http://localhost:5000/api/appointments/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Book dentist next Friday at 6pm"}'


3. Verify 6pm converts to 18:00 in response


🙏 Acknowledgments
EasyOCR for robust text extraction capabilities

Flask community for microservice best practices

Express.js team for reliable web framework

Postman for comprehensive API testing tools



