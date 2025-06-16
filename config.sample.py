"""
Sample configuration file for the Job Search Automation Framework.
Copy this file to config.local.py and update with your settings.
"""

# API Keys and Credentials
# Store these in .env file and load using python-dotenv
API_KEYS = {
    'linkedin_api_key': '',  # Load from environment
    'indeed_api_key': '',    # Load from environment
}

# Personal Information
PERSONAL_INFO = {
    'name': 'Your Name',
    'email': 'your.email@example.com',
    'phone': '+1234567890',
    'location': 'Your Location',
    'linkedin_url': 'https://linkedin.com/in/yourprofile',
}

# Job Search Parameters
SEARCH_PARAMS = {
    'keywords': [
        'Python',
        'Machine Learning',
        'Data Science',
    ],
    'locations': [
        'Remote',
        'New York',
        'San Francisco',
    ],
    'experience_level': ['Entry Level', 'Mid Level', 'Senior'],
    'job_types': ['Full-time', 'Contract'],
    'max_applications_per_day': 10,
    'max_results_per_search': 50,
}

# File Paths
PATHS = {
    'resume': 'assets/resume.pdf',
    'cover_letter': 'assets/cover_letter.pdf',
    'output_dir': 'output/',
    'log_file': 'logs/job_search.log',
}

# Application Settings
APPLICATION_SETTINGS = {
    'auto_apply': False,  # Set to True to enable automatic applications
    'require_keyword_match': True,
    'min_salary': 50000,
    'max_salary': 200000,
    'exclude_companies': [
        'company1.com',
        'company2.com',
    ],
}

# Database Settings
DATABASE = {
    'jobs_db': 'data/jobs_database.csv',
    'applied_jobs': 'data/applied_jobs.csv',
    'search_results': 'data/job_search_results.csv',
}

# Logging Configuration
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/job_search.log',
}

# Proxy Settings (if needed)
PROXY = {
    'use_proxy': False,
    'proxy_url': '',
    'proxy_username': '',
    'proxy_password': '',
}

# Rate Limiting
RATE_LIMITS = {
    'requests_per_minute': 30,
    'delay_between_requests': 2,  # seconds
} 