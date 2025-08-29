#GEMINI_UTILS.PY>>>>This file handles all API interactions with Gemini. I separated it from 
# the main UI so that the API logic can be reused or replaced easily.

import google.generativeai as genai     #to iteract with Gemini API
import os       #we want to load API keys from environment variables instead of user input.
from dotenv import load_dotenv      # loads variables from .env

load_dotenv()

def init_gemini():
    """Initialize Gemini API with the key from .env"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API Key not found in .env file...")
    genai.configure(api_key=api_key)     #Configures Gemini API once for the whole app.
#**init_gemini**>>>I abstracted the Gemini initialization into a function so it’s reusable.
#  I also added a validation step — if the key is missing, the app fails early 
# with a clear error instead of breaking later.


def generate_reply(style_instructions, email_text):
    """Send request to Gemini to draft an email reply."""
    prompt = f"""
You are Lana, an AI email Assistant.
reply to the following email based on the instuctions given. 

Style instructions: {style_instructions}

Email received: {email_text}

Draft a clear, polished reply:
"""
    model = genai.GenerativeModel("gemini-2.5-pro")
    response = model.generate_content(prompt)
    return response.text.strip()
#**generate_reply**>>>>Here I’m using prompt engineering. I explicitly tell the model
#  its role, the style, and the email content. That structure helps keep responses 
# consistent and relevant. I also clean up the output before returning 

