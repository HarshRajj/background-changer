import os
import json
import base64
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from google import genai
from io import BytesIO
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
def generate():
    try:
        # Handle preflight request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            return response

        # Get API key from environment
        API_KEY = os.environ.get("GEMINI_API_KEY")
        if not API_KEY:
            return jsonify({'error': 'API key not configured'}), 500

        # Parse JSON request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        option = data.get('option')
        image_data_base64 = data.get('image_data')
        mime_type = data.get('mime_type')

        if not all([option, image_data_base64, mime_type]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Decode base64 image data
        image_data = base64.b64decode(image_data_base64)

        # Initialize Gemini client
        client = genai.Client(api_key=API_KEY)

        # Different prompts based on option
        prompts = {
            'beach': "Transform this image by placing the main subject on a beautiful, sunny beach with clear blue water, white sand, palm trees, and tropical atmosphere. Keep the subject exactly as they are but change the background completely to a paradise beach setting.",
            'cosmic': "Transform this image by placing the main subject in outer space, with a backdrop of stars, nebulas, galaxies, and cosmic phenomena. Keep the subject exactly as they are but change the background to an amazing space scene with colorful nebulas and distant planets.Ensure that the image remains realistic, it must look like real",
            'cyberpunk': "Transform this image by placing the main subject in a bustling, futuristic cyberpunk cityscape at night with neon lights, flying vehicles, holographic advertisements, and rain-soaked streets. Keep the subject as they are but change the background to a sci-fi cyberpunk city.",
            'meme': "Turn this image into a finished internet meme in English. Add bold, funny meme text in classic Impact style at the top and bottom. The text should be short, witty, and very funny, matching the subject's expression or vibe. Make sure the joke is clear and instantly understandable, like a viral meme you'd see online. Do not leave placeholder text — write real English captions that make people laugh. Make it cartoony, colorful, and exaggerated to look meme-worthy."
        }

        if option not in prompts:
            return jsonify({'error': 'Invalid option selected'}), 400

        prompt_text = prompts[option]
        print(f"Processing option: {option}")

        # Create content for Gemini
        from google.genai import types
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt_text),
                    types.Part(inline_data=types.Blob(
                        mime_type=mime_type,
                        data=image_data
                    ))
                ],
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            system_instruction="Transform the input image according to the prompt while keeping the main subject intact."
        )

        print("Calling Gemini API...")
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=contents,
            config=generate_content_config,
        )

        if (response.candidates and 
            response.candidates[0].content and 
            response.candidates[0].content.parts):
            
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    data_buffer = part.inline_data.data
                    print("Generated image successfully!")
                    
                    # Create BytesIO object
                    img_io = BytesIO()
                    img_io.write(data_buffer)
                    img_io.seek(0)
                    
                    return send_file(img_io, mimetype=part.inline_data.mime_type)

        return jsonify({'error': 'No image generated'}), 500

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask test server...")
    print("📝 Make sure your GEMINI_API_KEY is set in .env file")
    print("🌐 Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
