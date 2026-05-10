import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-flash-latest')
try:
    response = model.generate_content("Hi")
    print(f"Success: {response.text}")
except Exception as e:
    print(f"Failed: {e}")
