import os
from flask import Flask, jsonify, request

from services.stt_service import convert_speech_to_text
from services.tts_service import convert_text_to_speech

# Initialize the Flask application
app = Flask(__name__)

@app.route('/api/v1/tts', methods=['POST'])
def tts():
    """
    Handle POST requests to /tts
    
    This endpoint is used to synthesize text-to-speech audio.
    The request should contain the text in the request body.
    
    Returns:
        A JSON response with the following format:
        {
            'status': 'success' | 'error',
            'message': 'A message describing the status of the request',
            'data': {
                'audio': 'The base64 encoded audio'
            }
        }
    """
    
    if request.method == 'POST':
        text = request.json.get('text')
        
        if not text:
            return jsonify({'status': 'error', 'message': 'No text provided'}), 400
        
        path = convert_text_to_speech(text)
        
        return jsonify({
            'status': 'success',
            'message': 'Text-to-speech synthesis successful',
            'data': {'path': path}
        })

@app.route('/api/v1/stt', methods=['POST'])
def stt():
    """
    Handle POST requests to /stt
    
    This endpoint is used to send audio for speech-to-text processing.
    The request should contain the path to the audio.
    
    Returns:
        A JSON response with the following format:
        {
            'status': 'success' | 'error',
            'message': 'A message describing the status of the request',
            'data': {
                'text': 'The text that was recognized from the audio'
            }
        }
    """
    print("> Request received for STT")
    print(request)

    if request.method == 'POST':
        print("Headers:", request.headers)
        print("JSON payload:", request.get_json())
        
        request_data = request.get_json()
        if not request_data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400
        
        file_path = request_data.get('filePath')
        print(f"File path: {file_path}")

        if not file_path or not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': 'File not found'}), 400
        
        try:
            # Process the audio file and get the recognized text
            result = convert_speech_to_text(file_path)
            
            return jsonify({
                'status': 'success',
                'message': 'Speech-to-text processing successful',
                'data': {'text': result}
            })
        except Exception as e:
            print("Error in processing:", e)
            return jsonify({'status': 'error', 'message': 'Failed to process the audio file'}), 500


# Run the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
