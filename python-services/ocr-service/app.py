# # Working One
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import requests
# from PIL import Image
# import io
# import re
# import easyocr
# import numpy as np

# app = Flask(__name__)
# CORS(app)

# # Initialize EasyOCR reader (English)
# print("🔄 Initializing EasyOCR...")
# try:
#     reader = easyocr.Reader(['en'])
#     print("✅ EasyOCR Ready!")
# except Exception as e:
#     print(f"❌ EasyOCR initialization failed: {e}")
#     reader = None

# @app.route('/health', methods=['GET'])
# def health_check():
#     status = "running" if reader else "failed"
#     return jsonify({"status": f"EasyOCR Service is {status}!"})

# @app.route('/extract-text', methods=['POST'])
# def extract_text():
#     try:
#         data = request.json
#         image_url = data.get('image_url', '')
        
#         print(f"📸 Processing image from: {image_url}")
        
#         if not image_url:
#             return jsonify({"error": "No image URL provided"}), 400
        
#         if not reader:
#             return jsonify({
#                 "raw_text": "OCR engine not available",
#                 "confidence": 0.10
#             })
        
#         # Download image
#         print("📥 Downloading image...")
#         response = requests.get(image_url, timeout=10)
#         response.raise_for_status()
        
#         # Open image
#         image = Image.open(io.BytesIO(response.content))
#         print(f"✅ Image loaded: {image.size} pixels")
        
#         # Convert to numpy array for EasyOCR
#         img_array = np.array(image)
        
#         # Perform OCR with EasyOCR
#         print("🔍 Performing OCR...")
#         results = reader.readtext(img_array)
        
#         # Extract text from results
#         extracted_text = " ".join([result[1] for result in results])
        
#         # Calculate confidence (average of all detections)
#         if results:
#             confidence = sum([result[2] for result in results]) / len(results)
#         else:
#             confidence = 0.1
#             extracted_text = "No text detected in image"
        
#         # Clean text
#         cleaned_text = re.sub(r'\s+', ' ', extracted_text).strip()
        
#         # Apply common OCR corrections
#         corrections = {
#             'Zpm': '3pm', 'zpm': '3pm', 
#             'next friday': 'next Friday', 'next monday': 'next Monday',
#             'nxt': 'next', 'appointm ent': 'appointment',
#             'dentistr': 'dentist', 'doktor': 'doctor'
#         }
        
#         for wrong, correct in corrections.items():
#             cleaned_text = cleaned_text.replace(wrong, correct)
        
#         print(f"✅ Text extracted: '{cleaned_text}'")
#         print(f"🎯 Confidence: {confidence:.2f}")
        
#         return jsonify({
#             "raw_text": cleaned_text,
#             "confidence": float(confidence)
#         })
        
#     except Exception as e:
#         print(f"❌ OCR Error: {str(e)}")
#         return jsonify({
#             "raw_text": f"Error: {str(e)}",
#             "confidence": 0.10
#         })

# if __name__ == '__main__':
#     print("🚀 EasyOCR Service Started on port 5001")
#     print("💡 Using EasyOCR for text extraction")
#     app.run(host='0.0.0.0', port=5001, debug=True)


from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from PIL import Image
import io
import re
import easyocr
import numpy as np

app = Flask(__name__)
CORS(app)

# Initialize EasyOCR reader
print("🔄 Initializing EasyOCR...")
try:
    reader = easyocr.Reader(['en'])
    print("✅ EasyOCR Ready!")
except Exception as e:
    print(f"❌ EasyOCR initialization failed: {e}")
    reader = None

@app.route('/health', methods=['GET'])
def health_check():
    status = "running" if reader else "failed"
    return jsonify({"status": f"EasyOCR Service is {status}!"})

# STEP 1: OCR/Text Extraction Only
@app.route('/extract-text', methods=['POST'])
def extract_text():
    try:
        data = request.json
        image_url = data.get('image_url', '')
        
        print(f"📸 STEP 1 - OCR Processing image from: {image_url}")
        
        if not image_url:
            return jsonify({"error": "No image URL provided"}), 400
        
        if not reader:
            return jsonify({
                "raw_text": "OCR engine not available",
                "confidence": 0.10
            })
        
        # Download image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Open image
        image = Image.open(io.BytesIO(response.content))
        
        # Perform OCR
        img_array = np.array(image)
        results = reader.readtext(img_array)
        
        # Extract text
        extracted_text = " ".join([result[1] for result in results])
        
        # Calculate confidence
        if results:
            confidence = sum([result[2] for result in results]) / len(results)
        else:
            confidence = 0.1
            extracted_text = "No text detected in image"
        
        # Clean text
        cleaned_text = re.sub(r'\s+', ' ', extracted_text).strip()
        
        # OCR corrections
        corrections = {
            'nxt': 'next', 'Zpm': '3pm', 'zpm': '3pm',
            'friday': 'Friday', 'monday': 'Monday'
        }
        
        for wrong, correct in corrections.items():
            cleaned_text = cleaned_text.replace(wrong, correct)
        
        print(f"✅ STEP 1 - Text extracted: '{cleaned_text}'")
        
        return jsonify({
            "raw_text": cleaned_text,
            "confidence": float(confidence)
        })
        
    except Exception as e:
        print(f"❌ OCR Error: {str(e)}")
        return jsonify({
            "raw_text": f"Error: {str(e)}",
            "confidence": 0.10
        })

if __name__ == '__main__':
    print("🚀 OCR Service Started on port 5001")
    app.run(host='0.0.0.0', port=5001, debug=True)