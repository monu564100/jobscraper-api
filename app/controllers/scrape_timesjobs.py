import requests
from app.helpers.response import ResponseHelper


def scrape_timesjobs(location='bangalore', limit='50'):
    """
    Scrape jobs from TimesJobs (uses their API)
    """
    
    # TimesJobs API endpoint
    # Location code for Bangalore: 198130
    location_codes = {
        'bangalore': '198130',
        'delhi': '199083',
        'mumbai': '199087',
        'hyderabad': '199096',
        'pune': '199100',
        'chennai': '199075'
    }
    
    location_code = location_codes.get(location.lower(), '198130')
    
    url = f'https://jobbuzz.timesjobs.com/jobbuzz/loadMoreJobs.json?companyIds=&locationnames={location_code}$&aosValues=&sortby=Y&from=filter&faids=&txtKeywords=&pSize={limit}'
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.timesjobs.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        jobs = data.get('jobsList', [])
        
        print(f"🔍 Found {len(jobs)} jobs from TimesJobs")
        
        results = []
        
        for job in jobs:
            try:
                # Extract skills
                key_skills = job.get('keySkills', [])
                skills_text = ', '.join([x.strip().strip('"') for x in key_skills])
                
                # Build link
                jd_url = job.get('jdUrl', '')
                link = f"http://www.timesjobs.com/candidate/{jd_url}" if jd_url else 'N/A'
                
                results.append({
                    'title': job.get('title', 'N/A'),
                    'company': job.get('companyName', 'N/A'),
                    'location': job.get('Location', location),
                    'salary': job.get('salary', 'Not disclosed'),
                    'description': job.get('jobDesc', '')[:200],
                    'skills': skills_text,
                    'experience': job.get('experience', '') + ' yrs' if job.get('experience') else '',
                    'end_date': job.get('expiry', ''),
                    'link': link,
                    'source': 'TimesJobs',
                    'posted_on': 'Recently'
                })
                
            except Exception as e:
                continue
        
        return ResponseHelper.success_response('Success scraping TimesJobs', {
            'jobs': results,
            'pagination': {'current_page': 1, 'last_page': 1, 'next_page': None}
        })
        
    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}", status_code=500)
