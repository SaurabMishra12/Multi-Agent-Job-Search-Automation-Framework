# Job search configuration
JOB_SEARCH_SITES = {
    'linkedin': 'https://www.linkedin.com/jobs/search',
    'indeed': 'https://www.indeed.com/jobs',
    'internshala': 'https://internshala.com/internships',
    'naukri': 'https://www.naukri.com',
    'ai-jobs.net': 'https://ai-jobs.net/search/', # Added based on resume
    'academickeys': 'https://academicjobs.com/jobs/search/', # Placeholder, might need specific search URL structure
    'huggingface': 'https://huggingface.co/jobs' # Added based on resume
}

# Candidate information
CANDIDATE_INFO = {
    'name': 'SAURAB MISHRA',
    'headline': 'Machine Learning Researcher | AI Researcher | Data Science Innovator | Technical Content Creator',
    'email': 'saurab23@iisertvm.ac.in',
    'phone': '+916201365207',
    'linkedin_url': 'https://www.linkedin.com/in/saurab-mishra-493a73178/',
    'portfolio_url': 'https://saurabmishra12.github.io/saurabmishra.github.io/',
    'youtube_url': 'https://www.youtube.com/@saurabmishra9376/videos',
    'medium_url': 'https://medium.com/@saurabmishra',
    'location': 'Thiruvananthapuram, Kerala',
    'professional_summary': 'Innovative AI researcher and IBM-certified data science specialist with strong expertise in machine learning, Retrieval Augmented Generation (RAG), reinforcement learning, and multi-agent systems. Experienced in technical content creation, advanced AI research, and real-world deployment. Research intern with publications under review at top-tier venues and a proven track record of delivering impactful, cutting-edge AI solutions.',
    'research_experience': [
        {
            'role': 'Research Intern',
            'supervisor': 'Prof. Kripabandhu Ghosh',
            'institution': 'Indian Institute of Science Education and Research Kolkata',
            'duration': '2024– Present (1+ Year)',
            'location': 'Remote',
            'responsibilities': [
                'Conducting advanced research in Multi-Agent Systems (MAS) for Large Language Models (LLMs), focusing on novel architectural designs and inter-agent communication protocols.',
                'Developing novel fine-tuning methodologies and Natural Language Processing (NLP) techniques to enhance model performance and mitigate biases in complex linguistic tasks.',
                'Prepared and submitted multiple research publications currently under review at top-tier AI/ML conferences, demonstrating significant contributions to the field.',
                'Contributing to cutting-edge research in ethical AI and human-AI interaction, exploring responsible AI development and user-centric design principles.'
            ]
        }
    ],
    'technical_skills': {
        'programming_languages_and_relevant_skills': ['Python', 'R', 'SQL', 'Data Science Techniques', 'Advanced Algorithm Design'],
        'ai_and_machine_learning': ['LLMs', 'RAG', 'RLHF', 'Multi-Agent Systems', 'Transformer Architectures', 'ML-Algorithms', 'Fine-tuning & NLP'],
        'frameworks_and_libraries': ['TensorFlow', 'PyTorch', 'Scikit-learn', 'Hugging Face', 'LangChain'],
        'cloud': ['AWS', 'Google Cloud', 'IBM Cloud']
    },
    'education': {
        'degree': 'BS-MS Dual Degree',
        'major': 'Computational and Applied Mathematics',
        'university': 'Indian Institute of Science Education and Research (IISER), Thiruvananthapuram',
        'graduation_year_range': '2023–2028',
        'location': 'India'
    },
    'technical_content_and_publications': {
        'technical_blog_writing': [
            'Medium Technical Blogger- @saurabmishra under Towards AI publication',
            'Authored comprehensive technical articles on AI/ML topics, reaching thousands of readers worldwide.',
            'Specialized content covering LLMs, RAG systems, and advanced ML architectures.'
        ],
        'educational_content_creation': [
            'Created in-depth YouTube playlist explaining Retrieval-Augmented Generation (RAG).',
            'Comprehensive technical tutorials bridging complex AI research with practical implementation.'
        ],
        'academic_publications': [
            'Multiple research papers on Multi-Agent Systems, Fine-tuning methodologies and NLP techniques currently under review at top-tier conferences.'
        ]
    },
    'innovative_projects': [
        {
            'name': 'Step Mentor: AI Educational Platform',
            'description': 'Developed an adaptive learning platform using fine-tuned multimodal LLM, improving user retention through personalized study plans and integrated many features.'
        },
        {
            'name': 'Research Project: Multi-Agent Systems for Enhanced LLM Performance',
            'description': 'Leveraged MAS frameworks to refine language model performance through collaboration and contextual optimization.',
            'key_innovations': ['Agent coordination', 'knowledge fusion', 'dynamic contextual systems']
        },
        {
            'name': 'Research Project: Reinforcement Learning from Human Feedback',
            'description': 'Advanced AI training pipelines by incorporating human feedback to align systems with ethical standards and values.',
            'key_innovations': ['Reinforcement learning algorithms', 'human-in-the-loop systems']
        },
        {
            'name': 'Retrieval-Augmented Generation Research Framework',
            'description': 'Revolutionized generative AI by integrating real-time knowledge retrieval, enabling contextually rich and accurate query responses.',
            'key_innovations': ['Knowledge graph integration', 'model retrieval optimization', 'hybrid generative systems']
        },
        {
            'name': 'SpaceX Falcon 9 Landing Prediction',
            'description': 'Machine learning model predicting first-stage rocket landings with accuracy, demonstrating potential for significant aerospace operational cost reduction.'
        },
        {
            'name': 'AI-Driven Medical Drug Recommendation System',
            'description': 'Implemented advanced Decision Trees to recommend prescriptions with accuracy, streamlining drug interaction analysis for improved healthcare delivery.'
        }
    ],
    'professional_certifications': [
        'IBM Data Science Professional Certification (2024)– Advanced Machine Learning Specialization',
        'Generative AI with Large Language Models Certification (2025)– LLMs Specialization'
    ],
    'club_and_extra_activities': [
        {
            'role': 'Founder & Head',
            'organization': 'Coding Club of IISER TVM',
            'institution': 'Indian Institute of Science Education and Research, Thiruvananthapuram',
            'duration': '2024 – Present',
            'achievements': [
                'Founded and scaled the Coding Club to 200 active members, establishing a collaborative environment recognized as the universitys fastest-growing student organization focused on real-world software development.',
                'Developed, deployed, and actively maintain the clubs official website with regular updates and feature rollouts.',
                'Spearheading three real-world software projects, coordinating and mentoring a team of 50 members for timely and impactful delivery.',
                'Designed and delivered structured technical courses and hands-on tutorials to enhance members technical proficiency.'
            ]
        }
    ],
    'research_interests': [
        'Machine Learning', 'Large Language Models', 'Multi-Agent Systems', 'Retrieval-Augmented Generation',
        'Reinforcement Learning with Human Feedback', 'Fine-tuning Methodologies', 'Natural Language Processing',
        'Computer Vision', 'Human-AI Interaction'
    ]
}

# File paths
RESUME_PATH = r'C:\Users\msaur\OneDrive\Desktop\MAS_towards AGI\assets\saurab final resume.pdf' # Raw string for Windows path
COVER_LETTER_TEMPLATE = 'assets/cover_letter_template.docx'

# Search parameters
SEARCH_KEYWORDS = [
    'research intern AI',
    'machine learning intern',
    'deep learning intern',
    'computer vision intern',
    'NLP intern',
    'data science intern',
    'python developer intern',
    'AI research intern',
    'multi-agent systems intern',
    'RAG intern',
    'reinforcement learning intern',
    'LLM intern',
    'generative AI intern',
    'summer research internship AI', # Made more general
    'machine learning research',
    'AI ethics research intern',
    'human-AI interaction research'
]

# Application settings
MAX_APPLICATIONS_PER_DAY = 5 # Increased slightly
SLEEP_BETWEEN_APPLICATIONS = 20  # seconds
MIN_WAIT_TIME = 3  # seconds
MAX_WAIT_TIME = 10  # seconds

# Browser settings (Primarily for Selenium if used, less critical for aiohttp/bs4)
BROWSER_CONFIG = {
    'window_size': '1920,1080',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', # Keep a modern user agent
    'accept_language': 'en-US,en;q=0.9',
    'headless': True # Set to False to see browser actions if Selenium is used
} 