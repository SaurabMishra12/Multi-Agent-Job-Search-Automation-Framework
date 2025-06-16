import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
import json
import uuid
from urllib.parse import quote_plus
import re

def parse_job_type(text: str) -> str:
    """A simple helper to parse job type from a string."""
    text_lower = text.lower()
    if re.search(r'\bremote\b', text_lower):
        return 'Remote'
    if re.search(r'\bhybrid\b', text_lower):
        return 'Hybrid'
    if re.search(r'\bpart-time\b', text_lower) or re.search(r'\bpart time\b', text_lower):
        return 'Part-time'
    if re.search(r'\bon-site\b', text_lower) or re.search(r'\bonsite\b', text_lower):
        return 'On-site'
    return 'Not Specified' # Default if no specific type is found

class JobBoardScrapers:
    @staticmethod
    async def search_linkedin(session: aiohttp.ClientSession, keyword: str) -> List[Dict]:
        """Search LinkedIn jobs."""
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={quote_plus(keyword)}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    jobs = []
                    
                    for job_card in soup.find_all('div', {'class': 'job-search-card'}):
                        location_text = job_card.find('span', {'class': 'job-search-card__location'}).text.strip()
                        job = {
                            'job_id': str(uuid.uuid4()),
                            'title': job_card.find('h3', {'class': 'base-search-card__title'}).text.strip(),
                            'company': job_card.find('h4', {'class': 'base-search-card__subtitle'}).text.strip(),
                            'location': location_text,
                            'link': job_card.find('a', {'class': 'base-card__full-link'})['href'],
                            'source': 'LinkedIn',
                            'job_type': parse_job_type(location_text)
                        }
                        jobs.append(job)
                    return jobs
        except Exception as e:
            logging.error(f"Error searching LinkedIn: {e}")
        return []

    @staticmethod
    async def search_indeed(session: aiohttp.ClientSession, keyword: str) -> List[Dict]:
        """Search Indeed jobs."""
        url = f"https://www.indeed.com/jobs?q={quote_plus(keyword)}&sort=date"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    jobs = []
                    
                    for job_card in soup.find_all('div', {'class': 'job_seen_beacon'}):
                        location_text = job_card.find('div', {'class': 'companyLocation'}).text.strip()
                        # Indeed sometimes puts job type in a separate div
                        job_type_div = job_card.find('div', class_='job-snippet') # Example class
                        job_type_text = location_text + (job_type_div.text if job_type_div else "")

                        job = {
                            'job_id': str(uuid.uuid4()),
                            'title': job_card.find('h2', {'class': 'jobTitle'}).text.strip(),
                            'company': job_card.find('span', {'class': 'companyName'}).text.strip(),
                            'location': location_text,
                            'link': 'https://www.indeed.com' + job_card.find('a')['href'],
                            'source': 'Indeed',
                            'job_type': parse_job_type(job_type_text)
                        }
                        jobs.append(job)
                    return jobs
        except Exception as e:
            logging.error(f"Error searching Indeed: {e}")
        return []

    @staticmethod
    async def search_internshala(session: aiohttp.ClientSession, keyword: str) -> List[Dict]:
        """Search Internshala jobs."""
        url = f"https://internshala.com/internships/keywords-{quote_plus(keyword)}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    jobs = []
                    
                    for job_card in soup.find_all('div', {'class': 'individual_internship'}):
                        location_text = job_card.find('a', {'class': 'location_link'}).text.strip()
                        # Internshala often has 'Work from home' or 'Part-time' labels
                        other_details_div = job_card.find('div', class_='other_detail_item_row')
                        job_type_text = location_text + (other_details_div.text if other_details_div else "")

                        job = {
                            'job_id': str(uuid.uuid4()),
                            'title': job_card.find('h3', {'class': 'heading_4_5'}).text.strip(),
                            'company': job_card.find('h4', {'class': 'heading_6'}).text.strip(),
                            'location': location_text,
                            'link': 'https://internshala.com' + job_card.find('a', {'class': 'view_detail_button'})['href'],
                            'source': 'Internshala',
                            'job_type': parse_job_type(job_type_text.replace("Work from home", "Remote"))
                        }
                        jobs.append(job)
                    return jobs
        except Exception as e:
            logging.error(f"Error searching Internshala: {e}")
        return []

    @staticmethod
    async def search_github_jobs(session: aiohttp.ClientSession, keyword: str) -> List[Dict]:
        """Search GitHub jobs."""
        url = f"https://jobs.github.com/positions.json?description={quote_plus(keyword)}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    jobs_data = await response.json()
                    return [{
                        'job_id': str(uuid.uuid4()),
                        'title': job['title'],
                        'company': job['company'],
                        'location': job['location'],
                        'link': job['url'],
                        'source': 'GitHub Jobs'
                    } for job in jobs_data]
        except Exception as e:
            logging.error(f"Error searching GitHub Jobs: {e}")
        return []

    @staticmethod
    async def search_research_gate(session: aiohttp.ClientSession, keyword: str) -> List[Dict]:
        """Search ResearchGate jobs."""
        url = f"https://www.researchgate.net/jobs/search?q={quote_plus(keyword)}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    jobs = []
                    
                    for job_card in soup.find_all('div', {'class': 'job-listing-item'}):
                        job = {
                            'job_id': str(uuid.uuid4()),
                            'title': job_card.find('h3').text.strip(),
                            'company': job_card.find('div', {'class': 'institution'}).text.strip(),
                            'location': job_card.find('div', {'class': 'location'}).text.strip(),
                            'link': 'https://www.researchgate.net' + job_card.find('a')['href'],
                            'source': 'ResearchGate'
                        }
                        jobs.append(job)
                    return jobs
        except Exception as e:
            logging.error(f"Error searching ResearchGate: {e}")
        return []

    @staticmethod
    async def search_google_careers(session: aiohttp.ClientSession, keyword: str) -> List[Dict]:
        """Search Google Careers."""
        url = f"https://careers.google.com/api/v3/search/?q={quote_plus(keyword)}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return [{
                        'job_id': str(uuid.uuid4()),
                        'title': job['title'],
                        'company': 'Google',
                        'location': job['location'],
                        'link': f"https://careers.google.com/jobs/results/{job['id']}",
                        'source': 'Google Careers'
                    } for job in data.get('jobs', [])]
        except Exception as e:
            logging.error(f"Error searching Google Careers: {e}")
        return []

    @staticmethod
    async def search_ycombinator_jobs(session: aiohttp.ClientSession, keyword: str) -> List[Dict]:
        """Search Y Combinator jobs."""
        url = f"https://www.ycombinator.com/jobs/search?q={quote_plus(keyword)}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    jobs = []
                    
                    job_listings_div = soup.find('div', class_='jobs-table')
                    if not job_listings_div:
                        # Try alternative structure if the primary one isn't found
                        # This is an example, YC structure might vary
                        job_elements = soup.select('a.job-listing') # More generic selector
                        for job_element in job_elements:
                            try:
                                title_tag = job_element.find(['h2', 'h3', 'div'], class_=[lambda x: x and 'title' in x.lower(), 'job-title'])
                                company_tag = job_element.find(['span', 'div'], class_=[lambda x: x and 'company' in x.lower(), 'company-name'])
                                location_tag = job_element.find(['span', 'div'], class_=[lambda x: x and 'location' in x.lower()])
                                link = job_element['href']
                                if not link.startswith('http'):
                                    link = 'https://www.ycombinator.com' + link

                                job = {
                                    'job_id': str(uuid.uuid4()),
                                    'title': title_tag.text.strip() if title_tag else 'N/A',
                                    'company': company_tag.text.strip() if company_tag else 'N/A',
                                    'location': location_tag.text.strip() if location_tag else 'N/A',
                                    'link': link,
                                    'source': 'Y Combinator'
                                }
                                if job['title'] != 'N/A': # Basic validation
                                    jobs.append(job)
                            except Exception as e:
                                logging.warning(f"Could not parse a YC job element: {e}")
                        return jobs

                    # Original parsing logic for 'jobs-table' structure
                    for job_card in job_listings_div.find_all('tr', class_='job'): # Assuming jobs are in table rows
                        try:
                            title_cell = job_card.find('td', class_='job-title')
                            company_cell = job_card.find('td', class_='job-company')
                            location_cell = job_card.find('td', class_='job-location')
                            link_tag = title_cell.find('a') if title_cell else None
                            
                            if not all([title_cell, company_cell, location_cell, link_tag]):
                                continue

                            job = {
                                'job_id': str(uuid.uuid4()),
                                'title': link_tag.text.strip(),
                                'company': company_cell.text.strip(),
                                'location': location_cell.text.strip(),
                                'link': 'https://www.ycombinator.com' + link_tag['href'],
                                'source': 'Y Combinator'
                            }
                            jobs.append(job)
                        except Exception as e:
                            logging.warning(f"Error parsing a YC job card: {e}")
                    return jobs
        except Exception as e:
            logging.error(f"Error searching Y Combinator Jobs: {e}")
        return []

    @staticmethod
    async def search_naukri_aio(session: aiohttp.ClientSession, keyword: str, location: str = "india") -> List[Dict]:
        """Search Naukri.com jobs using aiohttp. Location defaults to India."""
        # Constructing URL: Naukri uses URL path segments for keywords and location
        # Example: naukri.com/keyword-jobs-in-location or naukri.com/keyword-jobs
        keyword_formatted = quote_plus(keyword.lower().replace(' ', '-'))
        location_formatted = quote_plus(location.lower().replace(' ', '-'))
        
        if location:
            url = f"https://www.naukri.com/{keyword_formatted}-jobs-in-{location_formatted}"
        else:
            url = f"https://www.naukri.com/{keyword_formatted}-jobs"
        
        # Naukri might require specific headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        
        logging.info(f"Accessing Naukri URL: {url}")
        try:
            async with session.get(url, headers=headers) as response:
                logging.info(f"Naukri response status: {response.status}")
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml') # Using lxml for better parsing if available
                    jobs = []
                    
                    # Naukri's structure can be complex and changes. This is a common pattern.
                    # Look for article tags with class 'jobTuple' or similar
                    job_cards = soup.find_all('article', class_=lambda x: x and 'jobTuple' in x)
                    if not job_cards:
                        # Fallback: search for divs that might contain job info
                        job_cards = soup.select('div.jobTuple') # More specific div selector
                    
                    logging.info(f"Found {len(job_cards)} potential job cards on Naukri.")

                    for card in job_cards:
                        try:
                            title_tag = card.find('a', class_='title')
                            company_tag = card.find('a', class_='subTitle ellipsis fleft') 
                            location_tag = card.find('span', class_='ellipsis fleft locWdth') 
                            # Sometimes location is within a more generic span
                            if not location_tag:
                                location_tag = card.find('li', class_='fleft grey-text br2 placeHolderLi location')
                                if location_tag:
                                     loc_span = location_tag.find('span', class_='ellipsis fleft')
                                     location_text = loc_span.text.strip() if loc_span else 'N/A'
                                else:
                                    location_text = 'N/A'
                            else:
                                location_text = location_tag.text.strip()

                            job_link = title_tag['href'] if title_tag else None
                            job_title = title_tag.text.strip() if title_tag else 'N/A'
                            job_company = company_tag.text.strip() if company_tag else 'N/A'

                            if job_title != 'N/A' and job_link:
                                job = {
                                    'job_id': str(uuid.uuid4()),
                                    'title': job_title,
                                    'company': job_company,
                                    'location': location_text,
                                    'link': job_link,
                                    'source': 'Naukri.com'
                                }
                                jobs.append(job)
                        except Exception as e:
                            logging.warning(f"Could not parse all information from a Naukri job card: {e}")
                            continue
                    return jobs
                else:
                    logging.error(f"Naukri search failed with status {response.status}. URL: {url}")    
        except Exception as e:
            logging.error(f"Error searching Naukri.com: {e}. URL: {url}")
        return []

    @staticmethod
    async def search_ai_jobs_net(session: aiohttp.ClientSession, keyword: str) -> List[Dict]:
        """Search AI-Jobs.net."""
        url = f"https://ai-jobs.net/search/?q={quote_plus(keyword)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logging.info(f"Accessing AI-Jobs.net URL: {url}")
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    jobs = []
                    job_cards = soup.find_all('li', class_='list-group-item')
                    logging.info(f"Found {len(job_cards)} potential job cards on AI-Jobs.net.")
                    for card in job_cards:
                        try:
                            title_tag = card.find('h2', class_='h5').find('a') if card.find('h2', class_='h5') else None
                            company_span = card.find('span', class_='text-muted')
                            # Company might be within an <a> tag or just text
                            company_tag = company_span.find('a') if company_span else None
                            company_name = company_tag.text.strip() if company_tag else (company_span.text.split('at')[-1].strip() if company_span and 'at' in company_span.text else 'N/A')
                            
                            location_tag = card.find('span', attrs={"title": "Location"})
                            location_text = location_tag.text.strip() if location_tag else ''
                            tags = card.find_all('span', class_='badge')
                            tags_text = ' '.join([t.text for t in tags])
                            date_posted_tag = card.find('small', class_='text-muted')

                            if title_tag:
                                job_link = title_tag['href']
                                if not job_link.startswith('http'):
                                    job_link = 'https://ai-jobs.net' + job_link
                                job = {
                                    'job_id': str(uuid.uuid4()),
                                    'title': title_tag.text.strip(),
                                    'company': company_name,
                                    'location': location_text,
                                    'link': job_link,
                                    'source': 'AI-Jobs.net',
                                    'tags': [t.text.strip() for t in tags],
                                    'date_posted': date_posted_tag.text.strip() if date_posted_tag else 'N/A',
                                    'job_type': parse_job_type(location_text + ' ' + tags_text)
                                }
                                jobs.append(job)
                        except Exception as e:
                            logging.warning(f"Could not parse an AI-Jobs.net job card: {e}")
                    return jobs
        except Exception as e:
            logging.error(f"Error searching AI-Jobs.net: {e}")
        return []

    @staticmethod
    async def search_huggingface_jobs(session: aiohttp.ClientSession, keyword: str) -> List[Dict]:
        """Search Hugging Face Jobs."""
        # Hugging Face jobs are typically loaded via JS, direct scraping can be tricky.
        # They have an API endpoint, but it might require auth or change.
        # For now, let's try a pseudo-API approach if their job page structure is simple JSON or easily parsable.
        # This often means looking at network requests in browser dev tools.
        # As a fallback, a simple HTML parse attempt.
        url = f"https://huggingface.co/jobs?q={quote_plus(keyword)}" # This URL might be for display, not data
        # A more likely data source if available: e.g. https://huggingface.co/api/jobs?search=keyword
        # For this example, we'll assume a basic HTML structure if an API isn't readily available/documented.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logging.info(f"Accessing Hugging Face Jobs URL: {url}")
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    jobs = []
                    # Example selector - this WILL LIKELY CHANGE and needs inspection of actual HF jobs page
                    job_cards = soup.find_all('div', class_=lambda x: x and 'job-item' in x) 
                    logging.info(f"Found {len(job_cards)} potential job cards on Hugging Face Jobs.")
                    for card in job_cards:
                        try:
                            title_tag = card.find(['h2', 'h3', 'a'], class_=lambda x: x and ('title' in x or 'job-name' in x))
                            # Attempt to get a more specific company tag if possible
                            company_tag = card.find(['span','a', 'div'], class_=lambda x: x and ('company' in x or 'org' in x or 'employer' in x))
                            location_tag = card.find(['span', 'div'], class_=lambda x: x and 'location' in x)
                            location_text = location_tag.text.strip() if location_tag else ''
                            link_tag = card.find('a', href=True)

                            if title_tag and link_tag:
                                job_link = link_tag['href']
                                if not job_link.startswith('http'):
                                    job_link = 'https://huggingface.co' + job_link
                                job = {
                                    'job_id': str(uuid.uuid4()),
                                    'title': title_tag.text.strip(),
                                    'company': company_tag.text.strip() if company_tag else 'N/A',
                                    'location': location_text,
                                    'link': job_link,
                                    'source': 'Hugging Face Jobs',
                                    'job_type': parse_job_type(location_text)
                                }
                                jobs.append(job)
                        except Exception as e:
                            logging.warning(f"Could not parse a Hugging Face job card: {e}")
                    return jobs
        except Exception as e:
            logging.error(f"Error searching Hugging Face Jobs: {e}")
        return []

    @staticmethod
    async def search_academickeys(session: aiohttp.ClientSession, keyword: str) -> List[Dict]:
        """Search AcademicKeys.com jobs. This is a basic scraper and might need refinement."""
        # URL structure for AcademicKeys: search by keyword
        url = f"https://www.academickeys.com/search_jobs.php?action=search_jobs&query={quote_plus(keyword)}&job_type=&country=&state=&category=&discipline=&institution_name="
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logging.info(f"Accessing AcademicKeys URL: {url}")
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    jobs = []
                    # Selector for job listings - this is highly dependent on AcademicKeys' current HTML structure
                    # Often job listings are in tables or specific divs/articles
                    job_cards = soup.select('table tr[id^="job_ad_"]') # Example: selecting table rows with IDs starting with "job_ad_"
                    if not job_cards: # Fallback selector
                        job_cards = soup.find_all('div', class_='job-listing') # A more generic fallback
                    
                    logging.info(f"Found {len(job_cards)} potential job cards on AcademicKeys.")

                    for card in job_cards:
                        try:
                            title_tag = card.find('a', class_='job_title') # Look for a specific class for title link
                            if not title_tag:
                                title_tag = card.select_one('td:nth-of-type(1) a') # Fallback for table structure

                            company_tag = card.find('span', class_='job_institution')
                            if not company_tag:
                                company_tags = card.find_all('td')
                                if len(company_tags) > 1 : company_tag = company_tags[1] # Fallback for table
                            
                            location_tag = card.find('span', class_='job_location')
                            if not location_tag:
                                location_tags = card.find_all('td')
                                if len(location_tags) > 2: location_tag = location_tags[2] # Fallback for table
                                
                            location_text = location_tag.text.strip() if location_tag else ''

                            if title_tag and title_tag.get('href'):
                                job_link = title_tag['href']
                                if not job_link.startswith('http'):
                                    job_link = 'https://www.academickeys.com' + job_link.lstrip('.') # Remove leading dots if relative
                                
                                job = {
                                    'job_id': str(uuid.uuid4()),
                                    'title': title_tag.text.strip(),
                                    'company': company_tag.text.strip() if company_tag else 'N/A',
                                    'location': location_text,
                                    'link': job_link,
                                    'source': 'AcademicKeys.com',
                                    'job_type': parse_job_type(location_text)
                                }
                                jobs.append(job)
                        except Exception as e:
                            logging.warning(f"Could not parse an AcademicKeys job card: {e}. Card: {str(card)[:200]}") # Log part of card for debugging
                    return jobs
        except Exception as e:
            logging.error(f"Error searching AcademicKeys.com: {e}")
        return [] 