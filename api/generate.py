import os
import json
import base64
from http.server import BaseHTTPRequestHandler
from google import genai
from google.genai import types
# from google.genai.types import Content, Part, Blob
from io import BytesIO

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            # Get API key from environment
            API_KEY = os.environ.get("GEMINI_API_KEY")
            if not API_KEY:
                self._send_error(500, "API key not configured")
                return

            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            option = data.get('option')
            image_data_base64 = data.get('image_data')
            mime_type = data.get('mime_type')

            if not all([option, image_data_base64, mime_type]):
                self._send_error(400, "Missing required fields")
                return

            # Decode base64 image data
            image_data = base64.b64decode(image_data_base64)

            # Initialize Gemini client
            client = genai.Client(api_key=API_KEY)

            # Different prompts based on option
            prompts = {
                'beach': "Transform this image by placing the main subject on a beautiful, sunny beach with clear blue water, white sand, palm trees, and tropical atmosphere. Keep the subject exactly as they are but change the background completely to a paradise beach setting.",

                'cosmic': "Transform this image by placing the main subject in outer space, with a backdrop of stars, nebulas, galaxies, and cosmic phenomena. Keep the subject exactly as they are but change the background to an amazing space scene with colorful nebulas and distant planets. Ensure that the image looks completely realistic and immersive, as if the subject is truly floating in space.",

                'cyberpunk': "Transform this image by placing the main subject in a bustling, futuristic cyberpunk cityscape at night with neon lights, flying vehicles, holographic advertisements, and rain-soaked streets. Keep the subject as they are but change the background to a sci-fi cyberpunk city. Ensure that the image looks completely realistic and immersive, as if the subject is truly part of this vibrant, high-tech urban environment.",

                'meme': "Turn this image into a finished internet meme in English. Add bold, funny meme text in classic Impact style at the top and bottom. The text should be short, witty, and very funny, matching the subject's expression or vibe. Make sure the joke is clear and instantly understandable, like a viral meme you'd see online. Do not leave placeholder text — write real English captions that make people laugh. Make it cartoony, colorful, and exaggerated to look meme-worthy. Enhance the subject's expression or pose slightly to make it funnier, but keep them recognizable."
            }

            if option not in prompts:
                self._send_error(400, "Invalid option selected")
                return

            prompt_text = prompts[option]

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
                system_instruction=f"Transform the input image according to the prompt while keeping the main subject intact."
            )

            # Call Gemini API
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
                        
                        # Send image response
                        self.send_response(200)
                        self.send_header('Content-Type', part.inline_data.mime_type)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Content-Length', str(len(data_buffer)))
                        self.end_headers()
                        self.wfile.write(data_buffer)
                        return

            self._send_error(500, "No image generated")

        except Exception as e:
            self._send_error(500, f"Processing error: {str(e)}")

    def _send_error(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = json.dumps({'error': message})
        self.wfile.write(error_response.encode())
