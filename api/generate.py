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
                    'beach': "Transform this image by placing the main subject on a stunning, photorealistic tropical beach. The background should feature crystal-clear turquoise water, pristine white sand, lush green palm trees swaying gently, and a vibrant, sunny atmosphere. **The user's original pose, appearance, and identity should be preserved; however, minor adjustments to their lighting, shadows, or subtle interactions (e.g., a slight change in clothing texture to match the beach, or a reflection on wet sand) are acceptable to ensure seamless integration.** The goal is an immersive, high-definition image where the subject truly belongs on the beach.",
                
                    'forest': "Transform this image by placing the main subject deep within a hyper-realistic enchanted forest. The background should be a dense, vibrant woodland with towering ancient trees, dappled sunlight filtering through the canopy, rich green foliage, moss-covered rocks, and a sense of natural depth and atmosphere. **The user's original pose, appearance, and identity should be preserved; however, minor adjustments to their lighting, shadows, or subtle environmental interactions (e.g., a branch casting a shadow, or leaves subtly touching them) are acceptable to ensure perfect consistency.** Ensure the image makes them appear completely integrated and truly immersed in the realistic natural surroundings.",
                
                    'cyberpunk': "Transform this image by placing the main subject in a highly detailed, gritty, and photorealistic cyberpunk cityscape at night. The background should be a vibrant, rain-slicked urban environment filled with towering skyscrapers, intricate neon lights, holographic advertisements, and advanced flying vehicles. **The user's original pose, appearance, and identity should be preserved; however, minor adjustments to their lighting, reflections, or the texture/style of their clothing to better suit the futuristic aesthetic are acceptable to achieve seamless integration.** The subject should look genuinely part of this high-tech, dystopian scene.",
                
                    'meme': "Analyze the main subject and their expression/pose in this image and generate a hilarious, high-quality internet meme. The meme should feature bold, white Impact-style text at the top and bottom, with a black outline. The text must be short, witty, and extremely funny, directly relating to what's happening or the emotion conveyed by the subject. **The user's original appearance should be recognizable, but their expression or pose can be exaggerated, and their features made cartoony, colorful, and enhanced for maximum comedic effect, while still retaining their core identity.** The humor should be instant and viral-worthy, as if the image were specifically made to be a meme."
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
