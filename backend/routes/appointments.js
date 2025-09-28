const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { callOCRService, callEntityExtractionService, callNormalizationService } = require('../services/externalServices');

const router = express.Router();

// Create uploads directory if not exists
const uploadsDir = path.join(__dirname, '../uploads');
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/');
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + '-' + file.originalname);
    }
});

const upload = multer({ 
    storage: storage,
    fileFilter: function (req, file, cb) {
        if (file.mimetype.startsWith('image/')) {
            cb(null, true);
        } else {
            cb(new Error('Only image files are allowed!'), false);
        }
    },
    limits: {
        fileSize: 5 * 1024 * 1024 // 5MB limit
    }
});

// POST - Process appointment request with TEXT (text or imageUrl)
router.post('/process', async (req, res) => {
    try {
        const { text, imageUrl } = req.body;

        console.log('📨 Received request:', { text, imageUrl });

        if (!text && !imageUrl) {
            return res.status(400).json({
                status: "needs_clarification",
                message: "Please provide either text or imageUrl"
            });
        }

        let rawText = text;
        let ocrConfidence = 1.0;

        // Step 1: OCR Processing if image is provided
        if (imageUrl) {
            console.log('🖼️ Processing image with OCR...');
            const ocrResult = await callOCRService(imageUrl);
            rawText = ocrResult.raw_text;
            ocrConfidence = ocrResult.confidence;
            console.log('📝 Extracted text:', rawText);
        }

        if (!rawText || rawText.trim().length === 0) {
            return res.status(400).json({
                status: "needs_clarification",
                message: "No text found to process"
            });
        }

        // Step 2: Entity Extraction
        console.log('🔍 Extracting entities...');
        const entityResult = await callEntityExtractionService(rawText);
        const entities = entityResult.entities;
        const entitiesConfidence = entityResult.entities_confidence;
        console.log('📊 Entities found:', entities);

        // Check if essential entities are found
        if (!entities.date_phrase || !entities.time_phrase) {
            return res.json({
                status: "needs_clarification",
                message: "Could not detect date and time. Please be more specific."
            });
        }

        // Step 3: Normalization
        console.log('⏰ Normalizing date/time...');
        const normalizationResult = await callNormalizationService(entities);
        const normalized = normalizationResult.normalized;
        const normalizationConfidence = normalizationResult.normalization_confidence;
        console.log('📅 Normalized:', normalized);

        // Validate normalization results
        if (!normalized.date || !normalized.time) {
            return res.json({
                status: "needs_clarification",
                message: "Could not understand the date/time provided. Please try again."
            });
        }

        // Format department name
        const formattedDepartment = formatDepartment(entities.department);

        // Calculate overall confidence
        const overallConfidence = (
            (ocrConfidence * 0.4) + (entitiesConfidence * 0.3) + (normalizationConfidence * 0.3)
        ).toFixed(2);

        // Final response
        const response = {
            appointment: {
                department: formattedDepartment,
                date: normalized.date,
                time: normalized.time,
                tz: normalized.tz
            },
            status: "ok",
            confidence: parseFloat(overallConfidence),
            extracted_text: rawText,
            processing_steps: {
                ocr_confidence: ocrConfidence,
                entity_confidence: entitiesConfidence,
                normalization_confidence: normalizationConfidence
            }
        };

        console.log('✅ Processing completed successfully');
        res.json(response);
    } catch (err) {
        console.error('❌ Error processing appointment request:', err);
        res.status(500).json({ 
            status: "error", 
            message: "Internal server error. Please try again.",
            error: err.message 
        });
    }
});

// POST - Upload and process IMAGE file
router.post('/upload', upload.single('image'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                status: "needs_clarification",
                message: "No image file uploaded"
            });
        }

        console.log('📁 File uploaded:', req.file.filename);
        
        // Create accessible URL for the uploaded file
        const imageUrl = `${req.protocol}://${req.get('host')}/uploads/${req.file.filename}`;
        
        // Step 1: OCR Processing
        console.log('🖼️ Processing uploaded image with OCR...');
        const ocrResult = await callOCRService(imageUrl);
        const rawText = ocrResult.raw_text;
        const ocrConfidence = ocrResult.confidence;
        console.log('📝 Extracted text:', rawText);

        if (!rawText || rawText.trim().length === 0) {
            // Clean up uploaded file
            fs.unlinkSync(req.file.path);
            return res.status(400).json({
                status: "needs_clarification",
                message: "No text could be extracted from the image"
            });
        }

        // Step 2: Entity Extraction
        console.log('🔍 Extracting entities...');
        const entityResult = await callEntityExtractionService(rawText);
        const entities = entityResult.entities;
        const entitiesConfidence = entityResult.entities_confidence;
        console.log('📊 Entities found:', entities);

        if (!entities.date_phrase || !entities.time_phrase) {
            // Clean up uploaded file
            fs.unlinkSync(req.file.path);
            return res.json({
                status: "needs_clarification",
                message: "Could not detect date and time in the image text."
            });
        }

        // Step 3: Normalization
        console.log('⏰ Normalizing date/time...');
        const normalizationResult = await callNormalizationService(entities);
        const normalized = normalizationResult.normalized;
        const normalizationConfidence = normalizationResult.normalization_confidence;
        console.log('📅 Normalized:', normalized);

        if (!normalized.date || !normalized.time) {
            // Clean up uploaded file
            fs.unlinkSync(req.file.path);
            return res.json({
                status: "needs_clarification",
                message: "Could not understand the date/time in the image. Please try again."
            });
        }

        // Format department name
        const formattedDepartment = formatDepartment(entities.department);

        // Calculate overall confidence
        const overallConfidence = (
            (ocrConfidence * 0.4) + (entitiesConfidence * 0.3) + (normalizationConfidence * 0.3)
        ).toFixed(2);

        // Final response
        const response = {
            appointment: {
                department: formattedDepartment,
                date: normalized.date,
                time: normalized.time,
                tz: normalized.tz
            },
            status: "ok",
            confidence: parseFloat(overallConfidence),
            extracted_text: rawText,
            processing_steps: {
                ocr_confidence: ocrConfidence,
                entity_confidence: entitiesConfidence,
                normalization_confidence: normalizationConfidence
            }
        };

        console.log('✅ Image processing completed');
        
        // Clean up uploaded file after processing
        fs.unlinkSync(req.file.path);
        
        res.json(response);

    } catch (err) {
        console.error('❌ Error processing image:', err);
        
        // Clean up uploaded file in case of error
        if (req.file && fs.existsSync(req.file.path)) {
            fs.unlinkSync(req.file.path);
        }
        
        res.status(500).json({ 
            status: "error", 
            message: "Error processing image. Please try again.",
            error: err.message 
        });
    }
});

// GET - Processing history (optional)
router.get('/history', (req, res) => {
    // This would typically come from a database
    res.json({
        status: "ok",
        message: "History endpoint - implement database storage as needed",
        recent_processes: []
    });
});

// Helper function to format department name
function formatDepartment(department) {
    const departmentMap = {
        'dentist': 'Dentistry',
        'dental': 'Dentistry',
        'doctor': 'General Medicine',
        'physician': 'General Medicine',
        'dermatologist': 'Dermatology',
        'cardiologist': 'Cardiology',
        'ophthalmologist': 'Ophthalmology',
        'orthopedic': 'Orthopedics',
        'general': 'General Consultation'
    };
    return departmentMap[department.toLowerCase()] || 'General Consultation';
}

module.exports = router;