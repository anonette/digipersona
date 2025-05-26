import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4o"
    MAX_TOKENS = 500
    TEMPERATURE = 0.7
    
    # Rate Limiting
    REQUESTS_PER_SECOND = 3
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    # Database Configuration
    DATABASE_PATH = "data/personas.db"
    
    # Output Configuration
    OUTPUT_DIR = "output"
    PERSONAS_DIR = "output/personas"
    
    # Survey Configuration
    SURVEY_FILE = "survey.json"
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Create directories if they don't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.PERSONAS_DIR, exist_ok=True)