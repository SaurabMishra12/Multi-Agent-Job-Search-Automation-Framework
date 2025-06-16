"""
Environment and API key management utilities.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnvManager:
    def __init__(self):
        self.env_file = Path('.env')
        self.env_local_file = Path('.env.local')
        self._load_environment()

    def _load_environment(self):
        """Load environment variables from .env files."""
        # Load .env.local first (if exists) for local overrides
        if self.env_local_file.exists():
            load_dotenv(self.env_local_file)
            logger.info("Loaded environment from .env.local")
        
        # Load main .env file
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.info("Loaded environment from .env")
        else:
            logger.warning("No .env file found. Using system environment variables.")

    def get_api_key(self, key_name: str) -> str:
        """Safely retrieve an API key from environment variables."""
        key = os.getenv(key_name)
        if not key:
            raise ValueError(f"API key '{key_name}' not found in environment variables")
        return key

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value from environment variables."""
        return os.getenv(key, default)

    @staticmethod
    def create_env_template():
        """Create a template .env file if it doesn't exist."""
        template = """# API Keys
LINKEDIN_API_KEY=your_linkedin_api_key_here
INDEED_API_KEY=your_indeed_api_key_here

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=job_search
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Application Settings
DEBUG=False
LOG_LEVEL=INFO

# Proxy Settings (if needed)
USE_PROXY=False
PROXY_URL=
PROXY_USERNAME=
PROXY_PASSWORD=
"""
        env_file = Path('.env')
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write(template)
            logger.info("Created .env template file")
        else:
            logger.info(".env file already exists")

    @staticmethod
    def validate_required_keys(required_keys: list) -> Dict[str, bool]:
        """Validate that all required environment variables are set."""
        missing_keys = []
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            logger.error(f"Missing required environment variables: {', '.join(missing_keys)}")
            return {key: False for key in required_keys}
        
        return {key: True for key in required_keys}

# Create a singleton instance
env_manager = EnvManager() 