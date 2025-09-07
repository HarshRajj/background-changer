# Background Changer & Meme Generator

A simple web app that uses Gemini Flash 2.5 to change the background of an uploaded image or turn it into a meme. Deployable on Vercel, with a Flask test server for local development.

## Features
- Upload an image and choose from 4 effects:
  - Beach Day
  - Cosmic Voyager
  - Cyberpunk City
  - Make it a Meme
- Download the generated image
- Fast, modern UI (Tailwind CSS)
- Gemini Flash 2.5 API integration
- Vercel serverless backend (Python)

## Getting Started

### 1. Clone the Repository
```sh
git clone https://github.com/yourusername/background-changer.git
cd background-changer
```

### 2. Install Dependencies
Create a virtual environment and install requirements:
```sh
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 3. Set Up API Key
- Get your Gemini Flash 2.5 API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_api_key_here
```

### 4. Run Locally (Flask Test Server)
```sh
python test_server.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

### 5. Deploy to Vercel
- Push your code to GitHub
- Go to [vercel.com](https://vercel.com) and import your repo
- Set the `GEMINI_API_KEY` environment variable in Vercel dashboard
- Deploy!

## Project Structure
```
background-changer/
├── api/
│   └── generate.py         # Vercel serverless function
├── index.html              # Frontend UI
├── test_server.py          # Flask test server for local dev
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel config
├── .env                    # API key (local only)
└── README.md               # Project documentation
```

## Usage
1. Upload an image
2. Select an effect
3. Click "Generate"
4. Download your result

## Troubleshooting
- **API Key Error**: Make sure your `.env` file is correct and the key is valid
- **Dependencies**: Run `pip install -r requirements.txt` in your virtual environment
- **Vercel Issues**: Ensure your serverless function uses the correct format (`BaseHTTPRequestHandler`)

## License
MIT

---
Made with ❤️ using Gemini Flash 2.5
