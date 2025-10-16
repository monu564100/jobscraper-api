"""
LinkedIn Job Scraper
Requires: selenium, webdriver-manager, beautifulsoup4
Install: pip install selenium webdriver-manager beautifulsoup4
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re


class LinkedInScraper:
    def __init__(self, headless=True):
        """Initialize Chrome driver with options"""
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def parse_post_age(self, text):
        """Convert 'Posted 10 days ago' to days count"""
        if not text:
            return ''
        if 'hour' in text or 'minute' in text:
            return '0'
        numbers = re.findall(r'\d+', text)
        return numbers[0] if numbers else ''
    
    def extract_job_id(self, url):
        """Extract job ID from LinkedIn URL"""
        match = re.search(r'/view/(\d+)', url)
        return match.group(1) if match else ''
    
    def scrape_jobs(self, keyword, location='', filters=None):
        """
        Scrape LinkedIn jobs (public search, no login required)
        
        Args:
            keyword: Job title or keywords
            location: Location (city, country)
            filters: Dict with optional filters:
                - time_period: 'r86400' (24h), 'r604800' (week), 'r2592000' (month)
                - experience: '1' (Entry), '2' (Associate), '3' (Mid-Senior)
                - job_type: 'F' (Full-time), 'P' (Part-time), 'C' (Contract), 'I' (Internship)
                - work_type: '1' (On-site), '2' (Remote), '3' (Hybrid)
        
        Returns:
            List of job dictionaries
        """
        if not self.driver:
            self.setup_driver()
        
        try:
            # Build search URL
            base_url = 'https://www.linkedin.com/jobs/search/'
            params = {
                'keywords': keyword,
                'location': location,
                'sortBy': 'R'  # Most relevant
            }
            
            # Add filters if provided
            if filters:
                if 'time_period' in filters:
                    params['f_TP'] = filters['time_period']
                if 'experience' in filters:
                    params['f_E'] = filters['experience']
                if 'job_type' in filters:
                    params['f_JT'] = filters['job_type']
                if 'work_type' in filters:
                    params['f_WT'] = filters['work_type']
            
            # Build URL with parameters
            url_params = '&'.join([f'{k}={v}' for k, v in params.items()])
            url = f'{base_url}?{url_params}'
            
            print(f'🔍 Scraping LinkedIn: {url}')
            self.driver.get(url)
            
            # Wait for job listings to load
            time.sleep(3)
            
            # Scroll to load more jobs
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            
            # Parse job listings
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            job_cards = soup.find_all('div', class_='base-card')
            
            jobs = []
            for card in job_cards:
                try:
                    # Extract job link
                    link_elem = card.find('a', class_='base-card__full-link')
                    if not link_elem:
                        continue
                    
                    job_url = link_elem.get('href', '').split('?')[0]
                    job_id = self.extract_job_id(job_url)
                    
                    # Extract title
                    title_elem = card.find('h3', class_='base-search-card__title')
                    title = title_elem.text.strip() if title_elem else ''
                    
                    # Extract company
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    company = company_elem.text.strip() if company_elem else ''
                    
                    # Extract location
                    location_elem = card.find('span', class_='job-search-card__location')
                    job_location = location_elem.text.strip() if location_elem else ''
                    
                    # Extract posted date
                    date_elem = card.find('time', class_='job-search-card__listdate')
                    posted_date = date_elem.text.strip() if date_elem else 'Recently'
                    
                    if title and company:
                        jobs.append({
                            'id': job_id,
                            'title': title,
                            'company': company,
                            'location': job_location or 'Not specified',
                            'posted_on': posted_date,
                            'link': job_url,
                            'via': 'LinkedIn'
                        })
                
                except Exception as e:
                    print(f'Error parsing job card: {e}')
                    continue
            
            print(f'✅ Found {len(jobs)} jobs from LinkedIn')
            return jobs
        
        except Exception as e:
            print(f'❌ LinkedIn scraping error: {e}')
            return []
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None


# Route handler function
def scrape_linkedin_route(keyword, location='', filters=None, limit=25):
    """
    Route handler for LinkedIn scraping
    """
    scraper = LinkedInScraper(headless=True)
    
    try:
        jobs = scraper.scrape_jobs(keyword, location, filters)
        jobs = jobs[:limit]  # Apply limit
        
        return {
            'status': 'success',
            'message': f'Found {len(jobs)} jobs from LinkedIn',
            'data': {
                'jobs': jobs,
                'total': len(jobs),
                'source': 'LinkedIn'
            }
        }
    
    except Exception as e:
        return {
            'status': 'failed',
            'message': str(e),
            'data': {'jobs': []}
        }
    
    finally:
        scraper.close()
