import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    response = client.models.generate_content(
        model="models/gemini-3.6-flash",
        contents="Reply with exactly: API WORKING"
    )

    print(response.text)

except Exception as e:
    print(type(e))
    print(e)