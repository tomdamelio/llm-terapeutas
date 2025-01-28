"""
Configuration module for loading and managing environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Gemini API configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Flask configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = bool(int(os.getenv('FLASK_DEBUG', '0')))
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in environment variables") 