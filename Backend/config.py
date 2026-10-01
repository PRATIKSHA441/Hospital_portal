import os
from dotenv import load_dotenv

# Force loading from the root folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "hospital_portal")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") 