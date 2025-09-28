# # Working
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import re
# import random
# from datetime import datetime, timedelta

# app = Flask(__name__)
# CORS(app)

# print("✅ Entity Extraction Service starting...")

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "Entity Extraction Service is running!"})

# @app.route('/extract-entities', methods=['POST'])
# def extract_entities():
#     try:
#         data = request.json
#         text = data.get('text', '').strip()
        
#         print(f"🔍 Processing text: {text}")
        
#         if not text:
#             return jsonify({"error": "No text provided"}), 400
        
#         # Extract entities using regex
#         entities = extract_entities_with_regex(text)
        
#         # Calculate confidence
#         confidence = calculate_confidence(entities, text)
        
#         response = {
#             "entities": entities,
#             "entities_confidence": confidence
#         }
        
#         print(f"📊 Entities extracted: {entities}")
#         print(f"🎯 Confidence: {confidence}")
        
#         return jsonify(response)
        
#     except Exception as e:
#         print(f"❌ Entity Extraction Error: {str(e)}")
#         return jsonify({
#             "entities": {
#                 "date_phrase": "next Friday",
#                 "time_phrase": "3pm",
#                 "department": "general"
#             },
#             "entities_confidence": 0.60
#         }), 500

# def extract_entities_with_regex(text):
#     """Enhanced entity extraction with better patterns"""
#     text_lower = text.lower()
    
#     return {
#         "date_phrase": extract_date_with_regex(text),
#         "time_phrase": extract_time_with_regex(text),
#         "department": extract_department(text_lower)
#     }

# def extract_date_with_regex(text):
#     """Enhanced date extraction with better patterns"""
#     date_patterns = [
#         r'(next|this|coming)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
#         r'\b(tomorrow|today|yesterday)\b',
#         r'\b(next\s+week)\b',
#         r'\b(\d{1,2}(st|nd|rd|th)?\s+(of\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)',
#         r'\b((jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(st|nd|rd|th)?)',
#         r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
#         r'\b(\d{1,2}[/-]\d{1,2})',
#         r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
#     ]
    
#     for pattern in date_patterns:
#         match = re.search(pattern, text, re.IGNORECASE)
#         if match:
#             extracted = match.group().strip()
#             # If it's just a day name without "next" or "this", add "next"
#             if extracted.lower() in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
#                 return f"next {extracted}"
#             return extracted
    
#     # Final fallback - try to find any date-like pattern
#     fallback_patterns = [
#         r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
#         r'\b(\d+(st|nd|rd|th))\b'
#     ]
    
#     for pattern in fallback_patterns:
#         match = re.search(pattern, text, re.IGNORECASE)
#         if match:
#             extracted = match.group().strip()
#             if extracted.lower() in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
#                 return f"next {extracted}"
#             return extracted
    
#     return "next Friday"  # Final fallback

# def extract_time_with_regex(text):
#     """Enhanced time extraction"""
#     time_patterns = [
#         r'\b(\d{1,2}:\d{2}\s*(am|pm)?)\b',
#         r'\b(\d{1,2}\s*(am|pm))\b',
#         r'(at\s+\d{1,2}(:\d{2})?\s*(am|pm)?)\b',
#         r'\b(\d{1,2}(:\d{2})?\s*(o\'clock|oclock)?)\b',
#         r'\b(\d{1,2})\b(?![:\d])'  # Standalone hour numbers
#     ]
    
#     for pattern in time_patterns:
#         match = re.search(pattern, text, re.IGNORECASE)
#         if match:
#             time_text = match.group().strip()
#             # Remove leading "at"
#             if time_text.lower().startswith('at '):
#                 time_text = time_text[3:]
#             return time_text
    
#     return "3pm"  # Default fallback

# def extract_department(text_lower):
#     """Enhanced department extraction"""
#     department_keywords = {
#         'dentist': ['dentist', 'dental', 'teeth', 'tooth', 'cleaning', 'cavity'],
#         'doctor': ['doctor', 'physician', 'medical', 'checkup', 'general', 'check-up'],
#         'dermatologist': ['dermatologist', 'skin', 'rash', 'acne', 'pimple', 'eczema'],
#         'cardiologist': ['cardiologist', 'heart', 'cardio', 'blood pressure', 'bp', 'chest pain'],
#         'ophthalmologist': ['ophthalmologist', 'eye', 'vision', 'glasses', 'contact lens'],
#         'orthopedic': ['orthopedic', 'bone', 'joint', 'fracture', 'sports injury']
#     }
    
#     for dept, keywords in department_keywords.items():
#         if any(keyword in text_lower for keyword in keywords):
#             return dept
    
#     return 'general'

# def calculate_confidence(entities, text):
#     """Calculate confidence score for entity extraction"""
#     score = 0.0
#     factors = 0
    
#     # Check date quality
#     if entities["date_phrase"] and entities["date_phrase"] != "next Friday":
#         date_phrase = entities["date_phrase"].lower()
#         if any(word in date_phrase for word in ['next', 'tomorrow', 'today', 'yesterday']):
#             score += 0.4
#         elif any(day in date_phrase for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
#             score += 0.35
#         else:
#             score += 0.3
#         factors += 1
    
#     # Check time quality
#     if entities["time_phrase"] and entities["time_phrase"] != "3pm":
#         time_phrase = entities["time_phrase"].lower()
#         if any(indicator in time_phrase for indicator in ['am', 'pm', ':']):
#             score += 0.4
#         else:
#             score += 0.3
#         factors += 1
    
#     # Check department quality
#     if entities["department"] != "general":
#         score += 0.2
#         factors += 1
    
#     if factors > 0:
#         confidence = score / factors
#     else:
#         confidence = 0.3
    
#     # Add some randomness for demo (but cap at 0.95)
#     final_confidence = min(confidence + random.uniform(0.1, 0.3), 0.95)
#     return round(final_confidence, 2)

# if __name__ == '__main__':
#     print("🚀 Starting Entity Extraction Service on port 5002...")
#     print("✅ Using enhanced regex-based entity extraction")
#     app.run(host='0.0.0.0', port=5002, debug=True)







# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import re
# import random

# app = Flask(__name__)
# CORS(app)

# print("✅ Entity Extraction Service starting...")

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "Entity Extraction Service is running!"})

# # STEP 2: Entity Extraction Only
# @app.route('/extract-entities', methods=['POST'])
# def extract_entities():
#     try:
#         data = request.json
#         text = data.get('text', '').strip()
        
#         print(f"🔍 STEP 2 - Processing text: {text}")
        
#         if not text:
#             return jsonify({"error": "No text provided"}), 400
        
#         # Extract entities
#         entities = extract_entities_with_regex(text)
        
#         # Calculate confidence
#         confidence = calculate_confidence(entities, text)
        
#         response = {
#             "entities": entities,
#             "entities_confidence": confidence
#         }
        
#         print(f"✅ STEP 2 - Entities extracted: {entities}")
        
#         return jsonify(response)
        
#     except Exception as e:
#         print(f"❌ Entity Extraction Error: {str(e)}")
#         return jsonify({
#             "entities": {
#                 "date_phrase": "next Friday",
#                 "time_phrase": "3pm",
#                 "department": "general"
#             },
#             "entities_confidence": 0.60
#         }), 500

# # STEP 3: Normalization Only
# @app.route('/normalize', methods=['POST'])
# def normalize():
#     try:
#         data = request.json
#         entities = data.get('entities', {})
        
#         print(f"⏰ STEP 3 - Normalizing entities: {entities}")
        
#         if not entities:
#             return jsonify({"error": "No entities provided"}), 400
        
#         # Perform normalization
#         normalized = normalize_entities(entities)
        
#         response = {
#             "normalized": normalized,
#             "normalization_confidence": 0.90
#         }
        
#         print(f"✅ STEP 3 - Normalized: {normalized}")
        
#         return jsonify(response)
        
#     except Exception as e:
#         print(f"❌ Normalization Error: {str(e)}")
#         return jsonify({
#             "normalized": {
#                 "date": "2025-01-01",
#                 "time": "12:00",
#                 "tz": "Asia/Kolkata"
#             },
#             "normalization_confidence": 0.60
#         }), 500

# def extract_entities_with_regex(text):
#     """Extract entities using regex patterns"""
#     text_lower = text.lower()
    
#     return {
#         "date_phrase": extract_date_with_regex(text),
#         "time_phrase": extract_time_with_regex(text),
#         "department": extract_department(text_lower)
#     }

# def extract_date_with_regex(text):
#     """Extract date phrases using regex"""
#     date_patterns = [
#         r'(next|this|coming)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
#         r'\b(tomorrow|today|yesterday)\b',
#         r'\b(next\s+week)\b',
#         r'\b(\d{1,2}(st|nd|rd|th)?\s+(of\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)',
#         r'\b((jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(st|nd|rd|th)?)',
#         r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
#     ]
    
#     for pattern in date_patterns:
#         match = re.search(pattern, text, re.IGNORECASE)
#         if match:
#             extracted = match.group().strip()
#             # If it's just a day name, add "next"
#             if extracted.lower() in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
#                 return f"next {extracted}"
#             return extracted
    
#     return "next Friday"

# def extract_time_with_regex(text):
#     """Extract time phrases using regex"""
#     time_patterns = [
#         r'\b(\d{1,2}:\d{2}\s*(am|pm)?)\b',
#         r'\b(\d{1,2}\s*(am|pm))\b',
#         r'(at\s+\d{1,2}(:\d{2})?\s*(am|pm)?)\b',
#         r'\b(\d{1,2}(:\d{2})?\s*(o\'clock|oclock)?)\b'
#     ]
    
#     for pattern in time_patterns:
#         match = re.search(pattern, text, re.IGNORECASE)
#         if match:
#             time_text = match.group().strip()
#             if time_text.lower().startswith('at '):
#                 time_text = time_text[3:]
#             return time_text
    
#     return "3pm"

# def extract_department(text_lower):
#     """Extract department from text"""
#     department_keywords = {
#         'dentist': ['dentist', 'dental', 'teeth', 'tooth'],
#         'doctor': ['doctor', 'physician', 'medical', 'checkup'],
#         'dermatologist': ['dermatologist', 'skin', 'rash', 'acne'],
#         'cardiologist': ['cardiologist', 'heart', 'cardio']
#     }
    
#     for dept, keywords in department_keywords.items():
#         if any(keyword in text_lower for keyword in keywords):
#             return dept
    
#     return 'general'

# def normalize_entities(entities):
#     """Normalize entities to standard format"""
#     date_phrase = entities.get('date_phrase', 'next Friday')
#     time_phrase = entities.get('time_phrase', '3pm')
    
#     # Simple normalization logic - you can enhance this
#     date_map = {
#         'next friday': '2025-09-26',
#         'next monday': '2025-09-29',
#         'tomorrow': '2025-09-20',
#         'today': '2025-09-19'
#     }
    
#     time_map = {
#         '3pm': '15:00',
#         '3 pm': '15:00',
#         '4pm': '16:00',
#         '10am': '10:00',
#         '2:30pm': '14:30'
#     }
    
#     return {
#         "date": date_map.get(date_phrase.lower(), '2025-09-26'),
#         "time": time_map.get(time_phrase.lower(), '15:00'),
#         "tz": "Asia/Kolkata"
#     }

# def calculate_confidence(entities, text):
#     """Calculate confidence score"""
#     score = 0.0
#     factors = 0
    
#     if entities["date_phrase"] and entities["date_phrase"] != "next Friday":
#         score += 0.4
#         factors += 1
    
#     if entities["time_phrase"] and entities["time_phrase"] != "3pm":
#         score += 0.4
#         factors += 1
    
#     if entities["department"] != "general":
#         score += 0.2
#         factors += 1
    
#     if factors > 0:
#         confidence = score / factors
#     else:
#         confidence = 0.3
    
#     final_confidence = min(confidence + random.uniform(0.1, 0.3), 0.95)
#     return round(final_confidence, 2)

# if __name__ == '__main__':
#     print("🚀 Entity Extraction Service on port 5002...")
#     app.run(host='0.0.0.0', port=5002, debug=True)



from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

print("✅ Entity Extraction Service starting...")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Entity Extraction Service is running!"})

# STEP 2: Entity Extraction Only
@app.route('/extract-entities', methods=['POST'])
def extract_entities():
    try:
        data = request.json
        text = data.get('text', '').strip()
        
        print(f"🔍 STEP 2 - Processing text: {text}")
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Extract entities
        entities = extract_entities_with_regex(text)
        
        # Calculate confidence
        confidence = calculate_confidence(entities, text)
        
        response = {
            "entities": entities,
            "entities_confidence": confidence
        }
        
        print(f"✅ STEP 2 - Entities extracted: {entities}")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Entity Extraction Error: {str(e)}")
        return jsonify({
            "entities": {
                "date_phrase": "next Friday",
                "time_phrase": "3pm",
                "department": "general"
            },
            "entities_confidence": 0.60
        }), 500

# STEP 3: Normalization Only
@app.route('/normalize', methods=['POST'])
def normalize():
    try:
        data = request.json
        entities = data.get('entities', {})
        
        print(f"⏰ STEP 3 - Normalizing entities: {entities}")
        
        if not entities:
            return jsonify({"error": "No entities provided"}), 400
        
        # Perform normalization
        normalized = normalize_entities(entities)
        
        response = {
            "normalized": normalized,
            "normalization_confidence": 0.90
        }
        
        print(f"✅ STEP 3 - Normalized: {normalized}")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Normalization Error: {str(e)}")
        return jsonify({
            "normalized": {
                "date": "2025-01-01",
                "time": "12:00",
                "tz": "Asia/Kolkata"
            },
            "normalization_confidence": 0.60
        }), 500

def extract_entities_with_regex(text):
    """Extract entities using regex patterns"""
    text_lower = text.lower()
    
    return {
        "date_phrase": extract_date_with_regex(text),
        "time_phrase": extract_time_with_regex(text),
        "department": extract_department(text_lower)
    }

def extract_date_with_regex(text):
    """Extract date phrases using regex"""
    date_patterns = [
        r'(next|this|coming)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'\b(tomorrow|today|yesterday)\b',
        r'\b(next\s+week)\b',
        r'\b(\d{1,2}(st|nd|rd|th)?\s+(of\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)',
        r'\b((jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(st|nd|rd|th)?)',
        r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted = match.group().strip()
            # If it's just a day name, add "next"
            if extracted.lower() in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                return f"next {extracted}"
            return extracted
    
    return "next Friday"

def extract_time_with_regex(text):
    """Extract time phrases using regex"""
    time_patterns = [
        r'\b(\d{1,2}:\d{2}\s*(am|pm)?)\b',
        r'\b(\d{1,2}\s*(am|pm))\b',
        r'(at\s+\d{1,2}(:\d{2})?\s*(am|pm)?)\b',
        r'\b(\d{1,2}(:\d{2})?\s*(o\'clock|oclock)?)\b',
        r'\b(\d{1,2})\b(?![:\d])'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            time_text = match.group().strip()
            if time_text.lower().startswith('at '):
                time_text = time_text[3:]
            return time_text
    
    return "3pm"

def extract_department(text_lower):
    """Extract department from text"""
    department_keywords = {
        'dentist': ['dentist', 'dental', 'teeth', 'tooth'],
        'doctor': ['doctor', 'physician', 'medical', 'checkup'],
        'dermatologist': ['dermatologist', 'skin', 'rash', 'acne'],
        'cardiologist': ['cardiologist', 'heart', 'cardio']
    }
    
    for dept, keywords in department_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return dept
    
    return 'general'

def normalize_entities(entities):
    """Normalize entities to standard format"""
    date_phrase = entities.get('date_phrase', 'next Friday')
    time_phrase = entities.get('time_phrase', '3pm')
    
    print(f"🔄 Normalizing - Date: '{date_phrase}', Time: '{time_phrase}'")
    
    # Enhanced date mapping with actual calculations
    normalized_date = calculate_normalized_date(date_phrase)
    
    # Enhanced time mapping
    normalized_time = calculate_normalized_time(time_phrase)
    
    return {
        "date": normalized_date,
        "time": normalized_time,
        "tz": "Asia/Kolkata"
    }

def calculate_normalized_date(date_phrase):
    """Calculate actual date based on phrase"""
    date_phrase_lower = date_phrase.lower()
    today = datetime.now()
    
    # Date mapping with actual calculations
    if 'next friday' in date_phrase_lower:
        days_ahead = (4 - today.weekday() + 7) % 7  # Friday is 4
        if days_ahead == 0:  # Today is Friday
            days_ahead = 7   # Next Friday
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')
    
    elif 'next monday' in date_phrase_lower:
        days_ahead = (0 - today.weekday() + 7) % 7  # Monday is 0
        if days_ahead == 0:  # Today is Monday
            days_ahead = 7   # Next Monday
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')
    
    elif 'next tuesday' in date_phrase_lower:
        days_ahead = (1 - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')
    
    elif 'next wednesday' in date_phrase_lower:
        days_ahead = (2 - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')
    
    elif 'next thursday' in date_phrase_lower:
        days_ahead = (3 - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')
    
    elif 'next saturday' in date_phrase_lower:
        days_ahead = (5 - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')
    
    elif 'next sunday' in date_phrase_lower:
        days_ahead = (6 - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')
    
    elif 'tomorrow' in date_phrase_lower:
        target_date = today + timedelta(days=1)
        return target_date.strftime('%Y-%m-%d')
    
    elif 'today' in date_phrase_lower:
        return today.strftime('%Y-%m-%d')
    
    elif 'yesterday' in date_phrase_lower:
        target_date = today - timedelta(days=1)
        return target_date.strftime('%Y-%m-%d')
    
    else:
        # Default to next Friday if unknown
        days_ahead = (4 - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')

def calculate_normalized_time(time_phrase):
    """Convert time phrase to 24-hour format"""
    import re
    
    time_phrase_lower = time_phrase.lower().replace(' ', '')
    print(f"⏰ Processing time: '{time_phrase_lower}'")
    
    # Handle AM/PM times
    if 'pm' in time_phrase_lower:
        # Extract numbers before 'pm'
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?', time_phrase_lower)
        if time_match:
            hours = int(time_match.group(1))
            minutes = time_match.group(2) if time_match.group(2) else '00'
            
            # Convert to 24-hour format
            if hours < 12:
                hours += 12
            elif hours == 12:
                hours = 12  # 12 PM stays 12
            
            return f"{hours:02d}:{minutes}"
    
    elif 'am' in time_phrase_lower:
        # Extract numbers before 'am'
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?', time_phrase_lower)
        if time_match:
            hours = int(time_match.group(1))
            minutes = time_match.group(2) if time_match.group(2) else '00'
            
            # Convert to 24-hour format
            if hours == 12:
                hours = 0  # 12 AM becomes 00
            elif hours > 12:
                hours = hours  # Handle invalid cases
            
            return f"{hours:02d}:{minutes}"
    
    # Handle 24-hour format or simple numbers
    else:
        # Try to extract time pattern
        time_match = re.search(r'(\d{1,2}):(\d{2})', time_phrase_lower)
        if time_match:
            hours = int(time_match.group(1))
            minutes = time_match.group(2)
            
            # If it's 1-11 without AM/PM, assume PM for appointment context
            if 1 <= hours <= 11:
                hours += 12
                
            return f"{hours:02d}:{minutes}"
        
        # Handle simple hour numbers (e.g., "6", "10")
        hour_match = re.search(r'^(\d{1,2})$', time_phrase_lower)
        if hour_match:
            hours = int(hour_match.group(1))
            
            # Assume PM for appointment times (1-11 PM)
            if 1 <= hours <= 11:
                hours += 12
            elif hours == 12:
                hours = 12  # 12 PM
            # 13-23 remain as is (already in 24-hour)
            # 0 becomes 12 AM? Let's assume 0 means 12 AM
            elif hours == 0:
                hours = 0
                
            return f"{hours:02d}:00"
    
    # Default fallback
    return "15:00"

def calculate_confidence(entities, text):
    """Calculate confidence score for entity extraction"""
    score = 0.0
    factors = 0
    
    if entities["date_phrase"] and entities["date_phrase"] != "next Friday":
        date_phrase = entities["date_phrase"].lower()
        if any(word in date_phrase for word in ['next', 'tomorrow', 'today', 'yesterday']):
            score += 0.4
        elif any(day in date_phrase for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
            score += 0.35
        else:
            score += 0.3
        factors += 1
    
    if entities["time_phrase"] and entities["time_phrase"] != "3pm":
        time_phrase = entities["time_phrase"].lower()
        if any(indicator in time_phrase for indicator in ['am', 'pm', ':']):
            score += 0.4
        else:
            score += 0.3
        factors += 1
    
    if entities["department"] != "general":
        score += 0.2
        factors += 1
    
    if factors > 0:
        confidence = score / factors
    else:
        confidence = 0.3
    
    final_confidence = min(confidence + random.uniform(0.1, 0.3), 0.95)
    return round(final_confidence, 2)

if __name__ == '__main__':
    print("🚀 Entity Extraction Service on port 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True)