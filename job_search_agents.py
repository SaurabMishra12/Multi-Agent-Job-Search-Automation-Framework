import google.generativeai as genai
from typing import List, Dict, Optional
import pandas as pd
import asyncio
import aiohttp
import json
from datetime import datetime
from pathlib import Path
import logging
import uuid
from config import CANDIDATE_INFO, SEARCH_KEYWORDS, JOB_SEARCH_SITES
from job_board_scrapers import JobBoardScrapers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_search.log', mode='a'),
        logging.StreamHandler()
    ]
)

class JobSearchAgent:
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        
        # Define canonical_columns BEFORE it's used by _load_or_create_jobs_df
        self.canonical_columns = [
            'job_id', 'title', 'company', 'location', 'description',
            'requirements', 'salary_range', 'application_link', 'link',
            'source', 'discovery_date', 'status', 'relevance_score',
            'gemini_analysis', 'applied_date', 'response_received',
            'tags', 'date_posted', 'job_type'
        ]
        self.jobs_df = self._load_or_create_jobs_df()
        
    def _load_or_create_jobs_df(self) -> pd.DataFrame:
        """Load existing jobs CSV or create a new one with canonical columns."""
        csv_path = Path('jobs_database.csv')
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                for col in self.canonical_columns:
                    if col not in df.columns:
                        df[col] = None
                return df[self.canonical_columns]
            except pd.errors.EmptyDataError:
                logging.warning("jobs_database.csv is empty. Creating a new one.")
                return pd.DataFrame(columns=self.canonical_columns)
            except Exception as e:
                logging.error(f"Error loading jobs_database.csv: {e}. Creating a new one.")
                return pd.DataFrame(columns=self.canonical_columns)
        return pd.DataFrame(columns=self.canonical_columns)

    async def search_job_boards(self) -> List[Dict]:
        """Search multiple job boards concurrently."""
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = []
            candidate_location = CANDIDATE_INFO.get('location', None)
            if not candidate_location:
                logging.warning("Candidate location not specified in config.py, some job boards might require it or default to a broader search.")

            for keyword in SEARCH_KEYWORDS:
                logging.info(f"Creating search tasks for keyword: '{keyword}'")
                if 'linkedin' in JOB_SEARCH_SITES: tasks.append(JobBoardScrapers.search_linkedin(session, keyword))
                if 'indeed' in JOB_SEARCH_SITES: tasks.append(JobBoardScrapers.search_indeed(session, keyword))
                if 'internshala' in JOB_SEARCH_SITES: tasks.append(JobBoardScrapers.search_internshala(session, keyword))
                if 'naukri' in JOB_SEARCH_SITES: tasks.append(JobBoardScrapers.search_naukri_aio(session, keyword, location=candidate_location if candidate_location else "india"))
                if 'github' in JOB_SEARCH_SITES: tasks.append(JobBoardScrapers.search_github_jobs(session, keyword))
                if 'ycombinator' in JOB_SEARCH_SITES: tasks.append(JobBoardScrapers.search_ycombinator_jobs(session, keyword))
                if 'google_careers' in JOB_SEARCH_SITES: tasks.append(JobBoardScrapers.search_google_careers(session, keyword))
                if 'research_gate' in JOB_SEARCH_SITES: tasks.append(JobBoardScrapers.search_research_gate(session, keyword))
                if 'ai-jobs.net' in JOB_SEARCH_SITES: tasks.append(JobBoardScrapers.search_ai_jobs_net(session, keyword))
                if 'huggingface' in JOB_SEARCH_SITES: tasks.append(JobBoardScrapers.search_huggingface_jobs(session, keyword))
                if 'academickeys' in JOB_SEARCH_SITES: tasks.append(JobBoardScrapers.search_academickeys(session, keyword))
            
            if not tasks:
                logging.warning("No search tasks were created. Check JOB_SEARCH_SITES in config.py and scraper integrations.")
                return []

            results = await asyncio.gather(*tasks, return_exceptions=True)
            processed_jobs = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logging.error(f"A job search task failed: {result} (Task index: {i})")
                elif isinstance(result, list):
                    processed_jobs.extend(result)
                else:
                    logging.warning(f"Unexpected result type from job search task: {type(result)} (Task index: {i})")
            logging.info(f"Total jobs collected from all sources before filtering: {len(processed_jobs)}")
            return processed_jobs

    async def analyze_job_fit(self, job: Dict) -> Dict:
        """Use Gemini to analyze job fit and provide insights."""
        candidate_profile_str = json.dumps(CANDIDATE_INFO, indent=2, sort_keys=True)
        job_details_str = json.dumps(job, indent=2, sort_keys=True)

        prompt = f"""
        **Candidate Profile:**
        {candidate_profile_str}

        **Job Opportunity Details:**
        {job_details_str}

        **Analysis Task:**
        Please meticulously analyze the fit between the candidate's profile and the provided job opportunity.
        Consider the candidate's skills, research experience, projects, publications, certifications, and research interests.
        
        **Required Output Format (Strict JSON):**
        Return a JSON object with the following keys:
        - "match_score": An integer between 0 and 100, representing the overall compatibility.
        - "key_strengths_alignment": A list of strings detailing how the candidate's key strengths and experiences align with the job requirements.
        - "potential_gaps_or_areas_for_development": A list of strings identifying any potential gaps or areas where the candidate might need to develop further for this specific role, or aspects of the role that might not perfectly align with their primary interests.
        - "application_strategy_suggestions": A list of strings offering specific advice on how the candidate should tailor their application (e.g., which projects or skills to highlight).
        - "overall_recommendation": A string, one of "Strongly Recommend Apply", "Recommend Apply", "Consider Applying", "Likely Not a Good Fit".
        - "summary_for_candidate": A brief (2-3 sentences) summary explaining the rationale behind the recommendation for the candidate.
        
        Example of a good alignment point: "The candidate's extensive experience with Multi-Agent Systems and LLMs directly matches the core requirements for this AI Research Intern position."
        Example of a potential gap: "While the candidate has strong Python skills, the role emphasizes C++ for performance-critical components, which is not listed as a primary skill."
        Example of application strategy: "Highlight the 'Retrieval-Augmented Generation Research Framework' project in the cover letter, as it demonstrates direct experience with a key technology mentioned in the job description."

        Ensure the entire output is a single valid JSON object.
        """
        
        try:
            logging.info(f"Sending job analysis request to Gemini for job ID: {job.get('job_id', 'N/A')}, Title: {job.get('title', 'N/A')}")
            response = await self.model.generate_content_async(prompt)
            cleaned_response_text = response.text.strip()
            if cleaned_response_text.startswith("```json"):
                cleaned_response_text = cleaned_response_text[7:]
            if cleaned_response_text.endswith("```"):
                cleaned_response_text = cleaned_response_text[:-3]
            
            analysis_json = json.loads(cleaned_response_text)
            default_analysis = {
                "match_score": 0,
                "key_strengths_alignment": [],
                "potential_gaps_or_areas_for_development": [],
                "application_strategy_suggestions": [],
                "overall_recommendation": "Analysis Incomplete",
                "summary_for_candidate": "Could not fully parse Gemini analysis."
            }
            final_analysis = {**default_analysis, **analysis_json}

            logging.info(f"Successfully analyzed job {job.get('job_id', 'N/A')} with Gemini. Recommendation: {final_analysis.get('overall_recommendation')}")
            return {
                **job,
                'gemini_analysis': final_analysis,
                'relevance_score': int(final_analysis.get('match_score', 0))
            }
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError parsing Gemini response for job {job.get('job_id', 'N/A')}: {e}. Response text: {response.text}")
            return {**job, 'gemini_analysis': {'error': 'Failed to parse Gemini response as JSON', 'raw_text': response.text}, 'relevance_score': 0}
        except Exception as e:
            logging.error(f"Error analyzing job fit with Gemini for job {job.get('job_id', 'N/A')}: {str(e)}")
            return {**job, 'gemini_analysis': {'error': str(e)}, 'relevance_score': 0}

    def _extract_score(self, analysis: str) -> int:
        # This method is effectively deprecated by direct JSON parsing but kept for safety/other uses.
        try:
            import re
            scores = re.findall(r'(?:score:?\s*)(\d{1,3})', str(analysis).lower())
            if scores: return min(100, max(0, int(scores[0])))
        except Exception as e: logging.error(f"Error extracting score via regex: {e}")
        return 0

    async def process_new_jobs(self, jobs: List[Dict]):
        """Process, analyze new jobs and save them to the database."""
        new_jobs_count = 0
        for raw_job in jobs:
            if 'job_id' not in raw_job or not raw_job['job_id']:
                logging.warning(f"Job '{raw_job.get('title', 'Unknown Title')}' from source '{raw_job.get('source', 'Unknown Source')}' is missing a job_id. Assigning a new one.")
                raw_job['job_id'] = str(uuid.uuid4())

            if not self._is_duplicate_job(raw_job):
                new_jobs_count += 1
                logging.info(f"Processing new job: {raw_job.get('title')} (ID: {raw_job.get('job_id')})")
                analyzed_job = await self.analyze_job_fit(raw_job)
                
                # Add the fully analyzed job to the database with a 'new' status.
                self._add_to_database({**analyzed_job, 'status': 'new'}) 
        
        logging.info(f"Finished processing. Found and saved {new_jobs_count} new non-duplicate jobs to jobs_database.csv.")

    def _is_duplicate_job(self, job_from_scraper: Dict) -> bool:
        """Check if job already exists in database using job_id. Assumes job_from_scraper has a 'job_id'."""
        job_id = job_from_scraper.get('job_id')
        if not self.jobs_df.empty and 'job_id' in self.jobs_df.columns:
            if job_id:
                return str(job_id) in self.jobs_df['job_id'].astype(str).values
            else:
                logging.warning(f"Job from {job_from_scraper.get('source')} for '{job_from_scraper.get('title')}' is missing job_id for duplicate check. Falling back to content check.")
                return any(
                    (self.jobs_df['title'] == job_from_scraper.get('title')) &
                    (self.jobs_df['company'] == job_from_scraper.get('company')) &
                    (self.jobs_df['source'] == job_from_scraper.get('source'))
                )
        return False

    def _add_to_database(self, job: Dict):
        """Add or update job in database and save to CSV."""
        job_id = str(job.get('job_id'))
        
        if 'gemini_analysis' in job and isinstance(job['gemini_analysis'], dict):
            job['gemini_analysis'] = json.dumps(job['gemini_analysis'])

        if job.get('link') and not job.get('application_link'):
            job['application_link'] = job['link']

        new_row_data = {col: job.get(col) for col in self.canonical_columns}
        new_row_df = pd.DataFrame([new_row_data], columns=self.canonical_columns)

        if not self.jobs_df.empty and job_id in self.jobs_df['job_id'].astype(str).values:
            existing_job_index = self.jobs_df[self.jobs_df['job_id'].astype(str) == job_id].index
            self.jobs_df.loc[existing_job_index] = new_row_df.iloc[0].values
            logging.debug(f"Updated job ID {job_id} in database.")
        else:
            self.jobs_df = pd.concat([self.jobs_df, new_row_df], ignore_index=True)
            logging.debug(f"Added new job ID {job_id} to database.")
        
        if 'job_id' in self.jobs_df.columns:
             self.jobs_df['job_id'] = self.jobs_df['job_id'].astype(str)

        self.jobs_df.to_csv('jobs_database.csv', index=False)

    async def notify_user(self, job: Dict):
        """Notify user about high-potential job opportunity."""
        analysis_summary = job.get('gemini_analysis', {}).get('summary_for_candidate', 'No summary available.')
        overall_recommendation = job.get('gemini_analysis', {}).get('overall_recommendation', 'N/A')
        strengths_alignment = "\n".join([f"  - {s}" for s in job.get('gemini_analysis', {}).get('key_strengths_alignment', [])])
        potential_gaps = "\n".join([f"  - {g}" for g in job.get('gemini_analysis', {}).get('potential_gaps_or_areas_for_development', [])])
        application_suggestions = "\n".join([f"  - {s}" for s in job.get('gemini_analysis', {}).get('application_strategy_suggestions', [])])

        logging.info(f"""
        🌟 New High-Potential Opportunity! (Job ID: {job.get('job_id', 'N/A')}) 🌟
        
        Title: {job.get('title', 'N/A')}
        Company: {job.get('company', 'N/A')}
        Location: {job.get('location', 'N/A')}
        Source: {job.get('source', 'N/A')}
        Link: {job.get('application_link', job.get('link', 'N/A'))}
        Relevance Score (from Gemini): {job.get('relevance_score', 'N/A')}%
        Gemini Recommendation: {overall_recommendation}

        Gemini Summary for Candidate:
        {analysis_summary}

        Key Strengths Alignment:
{strengths_alignment if strengths_alignment else "  N/A"}

        Potential Gaps/Areas for Development:
{potential_gaps if potential_gaps else "  N/A"}

        Application Strategy Suggestions:
{application_suggestions if application_suggestions else "  N/A"}
        
        To apply, use the Job ID with the application command.
        (Example: apply_to_job(job_id="{job.get('job_id', 'N/A')}", user_confirmed=True) or via future interactive prompt)
        """)

    async def apply_to_job(self, job_id: str, user_confirmed: bool = False):
        """Apply to job if user confirms."""
        if not user_confirmed:
            logging.info(f"User did not confirm application for job ID: {job_id}")
            return False
            
        job_mask = self.jobs_df['job_id'] == str(job_id)
        
        if not self.jobs_df[job_mask].empty:
            job = self.jobs_df[job_mask].iloc[0]
            
            self.jobs_df.loc[job_mask, ['status', 'applied_date']] = ['applied', datetime.now().isoformat()]
            
            self.jobs_df.to_csv('jobs_database.csv', index=False)
            logging.info(f"User confirmed application for job: {job['title']} at {job['company']} (ID: {job_id}). Marked as 'applied'.")
            logging.info(f"To truly apply, please visit: {job.get('application_link', job.get('link', 'N/A'))}")
            return True
        else:
            logging.error(f"Could not find job with ID: {job_id} in the database to mark as applied.")
            return False

async def main():
    gemini_api_key = CANDIDATE_INFO.get('gemini_api_key')
    if not gemini_api_key:
        gemini_api_key = "AIzaSyDNS7h-1FOx5HuX5hFtK2dcjqHYx5wu1oo"
    
    if not gemini_api_key:
        logging.error("Gemini API key is not set. Please set it in config.py (CANDIDATE_INFO['gemini_api_key']) or directly in job_search_agents.py.")
        return

    agent = JobSearchAgent(gemini_api_key=gemini_api_key)
    
    logging.info("Starting automated job search and analysis process...")
    jobs_found = await agent.search_job_boards()
    
    if jobs_found:
        logging.info(f"Found a total of {len(jobs_found)} job listings from various boards.")
        await agent.process_new_jobs(jobs_found)
    else:
        logging.info("No new job listings found in this run.")
    
    logging.info("Script finished. All new jobs have been analyzed and saved to jobs_database.csv.")

if __name__ == "__main__":
    asyncio.run(main()) 