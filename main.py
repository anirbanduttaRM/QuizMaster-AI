import os
from dotenv import load_dotenv
from quiz_bot_frontend import QuizBotFrontend
from quiz_bot_backend import QuizBotBackend

# Load environment variables
load_dotenv()

# Fetch API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key is missing. Please check your .env file.")
    exit(1)

# Initialize backend and frontend
backend = QuizBotBackend(api_key)
frontend = QuizBotFrontend(backend)

# Run the frontend application
frontend.window.mainloop()