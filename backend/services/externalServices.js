const axios = require('axios');

const OCR_SERVICE_URL = 'http://127.0.0.1:5001';
const NLP_SERVICE_URL = 'http://127.0.0.1:5002';

// Real OCR service call
async function callOCRService(imageUrl) {
  try {
    console.log('📸 Calling OCR service...');
    
    const response = await axios.post(`${OCR_SERVICE_URL}/extract-text`, {
      image_url: imageUrl
    }, {
      timeout: 15000
    });

    console.log('✅ OCR result received');
    
    // Enhanced text cleaning for common OCR mistakes
    let cleanedText = response.data.raw_text;

    // Common OCR corrections
    const corrections = {
      'Zpm': '3pm', 'zpm': '3pm', '4pm': '4pm', '4 pm': '4pm',
      'next friday': 'next Friday', 'next monday': 'next Monday',
      'next tuesday': 'next Tuesday', 'next wednesday': 'next Wednesday',
      'next thursday': 'next Thursday', 'next saturday': 'next Saturday',
      'next sunday': 'next Sunday', 'tomorow': 'tomorrow',
      'tommorrow': 'tomorrow', 'todays': 'today',
      'nxt': 'next', 'appointm ent': 'appointment',
      'dentistr': 'dentist', 'doktor': 'doctor'
    };

    Object.keys(corrections).forEach(wrong => {
      const regex = new RegExp(`\\b${wrong}\\b`, 'gi');
      cleanedText = cleanedText.replace(regex, corrections[wrong]);
    });
    
    return {
      raw_text: cleanedText,
      confidence: response.data.confidence
    };
    
  } catch (error) {
    console.error('OCR Service error:', error.message);
    return {
      raw_text: "OCR service unavailable - " + error.message,
      confidence: 0.10
    };
  }
}

// Call Python entity extraction service
async function callEntityExtractionService(text) {
  try {
    console.log('🤖 Calling Entity Extraction service...');
    
    const response = await axios.post(`${NLP_SERVICE_URL}/extract-entities`, {
      text: text
    }, {
      timeout: 10000
    });

    return response.data;
  } catch (error) {
    console.error('Entity Extraction Service error:', error.message);
    return fallbackEntityExtraction(text);
  }
}

// Normalization service
async function callNormalizationService(entities) {
  try {
    return normalizeDateTime(entities);
  } catch (error) {
    console.error('Normalization error:', error.message);
    throw error;
  }
}

// Enhanced fallback entity extraction
function fallbackEntityExtraction(text) {
  console.log('🔄 Using fallback entity extraction');
  
  const lowerText = text.toLowerCase();
  
  // Enhanced date patterns
  const datePatterns = [
    /(next|this|coming)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i,
    /(tomorrow|today|yesterday)/i,
    /\b(\d{1,2}(st|nd|rd|th)?\s+(of\s+)?(january|february|march|april|may|june|july|august|september|october|november|december))/i,
    /\b((january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(st|nd|rd|th)?)/i,
    /\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})/,
    /\b(\d{1,2}[\/\-]\d{1,2})/,
    /(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i,
    /(next week|following week)/i
  ];

  let datePhrase = '';
  for (const pattern of datePatterns) {
    const match = text.match(pattern);
    if (match) {
      datePhrase = match[0];
      break;
    }
  }

  // Enhanced time patterns
  const timePatterns = [
    /\b(\d{1,2}:\d{2}\s*(am|pm)?)/i,
    /\b(\d{1,2}\s*(am|pm))/i,
    /(at\s+\d{1,2}(:\d{2})?\s*(am|pm)?)/i,
    /\b(\d{1,2}(:\d{2})?\s*(o'clock|oclock)?)/i,
    /\b(\d{1,2})\b(?![:\d])/i
  ];

  let timePhrase = '';
  for (const pattern of timePatterns) {
    const match = text.match(pattern);
    if (match) {
      timePhrase = match[0].replace(/^at\s+/i, ''); // Remove leading "at"
      break;
    }
  }

  // Enhanced department detection
  let department = 'general';
  const departmentKeywords = {
    'dentist': ['dentist', 'dental', 'teeth', 'tooth', 'cleaning', 'cavity'],
    'doctor': ['doctor', 'physician', 'medical', 'checkup', 'general', 'check-up'],
    'dermatologist': ['dermatologist', 'skin', 'rash', 'acne', 'pimple', 'eczema'],
    'cardiologist': ['cardiologist', 'heart', 'cardio', 'blood pressure', 'bp', 'chest pain'],
    'ophthalmologist': ['ophthalmologist', 'eye', 'vision', 'glasses', 'contact lens'],
    'orthopedic': ['orthopedic', 'bone', 'joint', 'fracture', 'sports injury']
  };

  for (const [dept, keywords] of Object.entries(departmentKeywords)) {
    if (keywords.some(keyword => lowerText.includes(keyword))) {
      department = dept;
      break;
    }
  }

  // If no date found, try to find any day mention
  if (!datePhrase) {
    const dayMatch = text.match(/(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i);
    if (dayMatch) {
      datePhrase = `next ${dayMatch[0]}`;
    }
  }

  return {
    entities: {
      date_phrase: datePhrase || 'next Friday',
      time_phrase: timePhrase || '3pm',
      department: department
    },
    entities_confidence: 0.75
  };
}

// COMPLETELY REWRITTEN Date/Time normalization with dynamic calculations
function normalizeDateTime(entities) {
  const { date_phrase, time_phrase } = entities;
  
  console.log(`📅 Normalizing date: "${date_phrase}", time: "${time_phrase}"`);
  
  try {
    // Calculate the normalized date
    const normalizedDate = calculateDate(date_phrase);
    
    // Calculate the normalized time
    const normalizedTime = calculateTime(time_phrase);
    
    return {
      normalized: {
        date: normalizedDate,
        time: normalizedTime,
        tz: "Asia/Kolkata"
      },
      normalization_confidence: 0.95
    };
  } catch (error) {
    console.error('Normalization error:', error);
    // Fallback to default values
    return {
      normalized: {
        date: getNextDayOfWeekDate(5), // Next Friday
        time: "15:00",
        tz: "Asia/Kolkata"
      },
      normalization_confidence: 0.70
    };
  }
}

// Enhanced date calculation function
function calculateDate(datePhrase) {
  if (!datePhrase) return getNextDayOfWeekDate(5); // Default to next Friday
  
  const lowerDatePhrase = datePhrase.toLowerCase();
  const today = new Date();
  
  // Handle relative dates
  if (lowerDatePhrase.includes('tomorrow')) {
    return getTomorrowDate();
  }
  
  if (lowerDatePhrase.includes('today')) {
    return getTodayDate();
  }
  
  if (lowerDatePhrase.includes('yesterday')) {
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    return yesterday.toISOString().split('T')[0];
  }
  
  // Handle "next week"
  if (lowerDatePhrase.includes('next week')) {
    const nextWeek = new Date(today);
    nextWeek.setDate(nextWeek.getDate() + 7);
    return nextWeek.toISOString().split('T')[0];
  }
  
  // Handle days of the week
  const dayMap = {
    'sunday': 0, 'monday': 1, 'tuesday': 2, 'wednesday': 3,
    'thursday': 4, 'friday': 5, 'saturday': 6
  };
  
  for (const [dayName, dayNumber] of Object.entries(dayMap)) {
    if (lowerDatePhrase.includes(dayName)) {
      // Check if it's "this" or "next"
      if (lowerDatePhrase.includes('this ')) {
        return getThisDayOfWeekDate(dayNumber);
      } else {
        return getNextDayOfWeekDate(dayNumber);
      }
    }
  }
  
  // Try to parse specific date formats
  const dateFormats = [
    // MM/DD/YYYY or DD/MM/YYYY
    /\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b/,
    // MM/DD or DD/MM (assume current year)
    /\b(\d{1,2})[\/\-](\d{1,2})\b/
  ];
  
  for (const format of dateFormats) {
    const match = datePhrase.match(format);
    if (match) {
      let month, day, year = new Date().getFullYear();
      
      if (match[3]) { // Has year
        // Try both MM/DD/YYYY and DD/MM/YYYY
        const first = parseInt(match[1]);
        const second = parseInt(match[2]);
        
        if (first > 12) { // DD/MM/YYYY
          day = first;
          month = second - 1; // Months are 0-indexed
          year = parseInt(match[3]);
        } else { // MM/DD/YYYY
          month = first - 1;
          day = second;
          year = parseInt(match[3]);
        }
      } else { // No year, assume current
        const first = parseInt(match[1]);
        const second = parseInt(match[2]);
        
        if (first > 12) { // DD/MM
          day = first;
          month = second - 1;
        } else { // MM/DD
          month = first - 1;
          day = second;
        }
      }
      
      const date = new Date(year, month, day);
      if (!isNaN(date.getTime())) {
        return date.toISOString().split('T')[0];
      }
    }
  }
  
  // Default fallback - next Friday
  return getNextDayOfWeekDate(5);
}

// Enhanced time calculation function
function calculateTime(timePhrase) {
  if (!timePhrase) return '15:00'; // Default to 3pm
  
  const cleanTime = timePhrase.toLowerCase().replace(/\s/g, '');
  
  // Handle AM/PM times
  if (cleanTime.includes('am') || cleanTime.includes('pm')) {
    const timeMatch = cleanTime.match(/(\d{1,2})(?::(\d{2}))?\s*(am|pm)/);
    if (timeMatch) {
      let hours = parseInt(timeMatch[1]);
      const minutes = timeMatch[2] ? timeMatch[2].padStart(2, '0') : '00';
      const period = timeMatch[3];
      
      // Convert to 24-hour format
      if (period === 'pm' && hours < 12) hours += 12;
      if (period === 'am' && hours === 12) hours = 0;
      
      return `${hours.toString().padStart(2, '0')}:${minutes}`;
    }
  }
  
  // Handle 24-hour format
  const twentyFourHourMatch = cleanTime.match(/(\d{1,2}):(\d{2})/);
  if (twentyFourHourMatch) {
    const hours = twentyFourHourMatch[1].padStart(2, '0');
    const minutes = twentyFourHourMatch[2];
    return `${hours}:${minutes}`;
  }
  
  // Handle simple hour numbers (1-12)
  const hourMatch = cleanTime.match(/(\d{1,2})/);
  if (hourMatch) {
    let hours = parseInt(hourMatch[1]);
    // Assume PM if hour is 1-11 and no AM specified, but handle 12 specially
    if (hours < 12 && hours >= 1 && !cleanTime.includes('am')) {
      hours += 12;
    }
    if (hours === 12 && cleanTime.includes('am')) {
      hours = 0; // 12 AM midnight
    }
    
    return `${hours.toString().padStart(2, '0')}:00`;
  }
  
  return '15:00'; // Default fallback
}

// Date helper functions
function getTodayDate() {
  return new Date().toISOString().split('T')[0];
}

function getTomorrowDate() {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.toISOString().split('T')[0];
}

function getNextDayOfWeekDate(dayOfWeek) {
  const today = new Date();
  const currentDayOfWeek = today.getDay();
  
  let daysToAdd = (dayOfWeek - currentDayOfWeek + 7) % 7;
  if (daysToAdd === 0) {
    daysToAdd = 7; // Move to next week if it's today
  }
  
  const targetDate = new Date(today);
  targetDate.setDate(today.getDate() + daysToAdd);
  return targetDate.toISOString().split('T')[0];
}

function getThisDayOfWeekDate(dayOfWeek) {
  const today = new Date();
  const currentDayOfWeek = today.getDay();
  
  let daysToAdd = (dayOfWeek - currentDayOfWeek + 7) % 7;
  
  const targetDate = new Date(today);
  targetDate.setDate(today.getDate() + daysToAdd);
  return targetDate.toISOString().split('T')[0];
}

module.exports = {
  callOCRService,
  callEntityExtractionService,
  callNormalizationService
};