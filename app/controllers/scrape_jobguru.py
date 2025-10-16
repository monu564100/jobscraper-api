import requests
from bs4 import BeautifulSoup
from html import unescape
from app.helpers.response import ResponseHelper


def scrape_jobguru():
    """
    Scrape jobs from JobGuru (uses their API)
    """
    
    url = 'https://www.jobguru.in/jobs_response.php'
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.jobguru.in/'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        jobs = data.get('jobs', [])
        
        print(f"🔍 Found {len(jobs)} jobs from JobGuru")
        
        results = []
        
        for job in jobs:
            try:
                # Extract title from HTML
                title_html = job.get('title', '')
                soup = BeautifulSoup(title_html, 'lxml')
                title = ' '.join(soup.stripped_strings) if soup else 'N/A'
                
                # Clean description
                description = job.get('description', '').lstrip('Job Description')
                description = unescape(description.replace('\n', ' ').strip())
                
                # Build link
                job_id = job.get('id', '')
                slug = job.get('slug', '')
                link = f"https://www.jobguru.in/job/{job_id}/{slug}" if job_id and slug else 'N/A'
                
                # Clean location
                location = job.get('locations', 'India')
                location = unescape(location.replace('\n', ' ').strip())
                
                results.append({
                    'title': title,
                    'company': job.get('company', 'N/A'),
                    'location': location,
                    'salary': job.get('salary', 'Not disclosed'),
                    'type': job.get('shift', 'Full-time'),
                    'description': description[:200] if description else '',
                    'link': link,
                    'start_date': job.get('date', ''),
                    'source': 'JobGuru',
                    'experience': ''
                })
                
            except Exception as e:
                continue
        
        return ResponseHelper.success_response('Success scraping JobGuru', {
            'jobs': results,
            'pagination': {'current_page': 1, 'last_page': 1, 'next_page': None}
        })
        
    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}", status_code=500)
