"""
Configuration module for loading and managing environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Gemini API configuration
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

# Flask configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = bool(int(os.getenv('FLASK_DEBUG', '0')))
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in environment variables")

# Other configuration settings can be added here
DEBUG = True 