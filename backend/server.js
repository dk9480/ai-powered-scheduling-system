const express = require('express');
const cors = require('cors');
const appointmentRoutes = require('./routes/appointments');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5000;

// Create uploads directory if not exists
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
    console.log('📁 Created uploads directory');
}

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Serve uploaded images statically
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Routes
app.use('/api/appointments', appointmentRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        timestamp: new Date().toISOString(),
        service: 'Appointment Scheduler API'
    });
});

// Root endpoint
app.get('/', (req, res) => {
    res.json({ 
        message: '🚀 Appointment Scheduler API is running!',
        version: '1.0.0',
        endpoints: {
            'POST /api/appointments/process': 'Process text or image URL request',
            'POST /api/appointments/upload': 'Upload and process image file',
            'GET /api/appointments/history': 'Get processing history',
            'GET /health': 'Health check'
        },
        services: {
            'OCR Service': 'http://localhost:5001',
            'NLP Service': 'http://localhost:5002'
        }
    });
});

// 404 handler - FIXED: Use proper Express 404 handling
app.use((req, res) => {
    res.status(404).json({
        status: "error",
        message: "Endpoint not found",
        path: req.path
    });
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('❌ Server Error:', error);
    res.status(500).json({
        status: "error",
        message: "Internal server error",
        error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Server running on port ${PORT}`);
    console.log(`📍 Local: http://localhost:${PORT}`);
    console.log(`🌐 Network: http://0.0.0.0:${PORT}`);
    console.log(`📊 OCR Service: http://localhost:5001`);
    console.log(`🔍 NLP Service: http://localhost:5002`);
    console.log(`🖼️ Uploads served from: http://localhost:${PORT}/uploads/`);
    console.log(`💡 Health check: http://localhost:${PORT}/health`);
    console.log(`📝 API Documentation: http://localhost:${PORT}/`);
});

module.exports = app;