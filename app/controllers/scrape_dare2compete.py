import requests
from bs4 import BeautifulSoup
from app.helpers.response import ResponseHelper


def scrape_dare2compete(opportunity_type='internships', page='1'):
    """
    Scrape opportunities from Dare2Compete (uses their API)
    
    Args:
        opportunity_type: Type of opportunity (default: 'internships')
        page: Page number (default: '1')
    """
    
    # Dare2Compete has a public API!
    url = f'https://api.dare2compete.com/api/opportunity/search?opportunity={opportunity_type}&sort=latest&page={page}'
    
    try:
        # Make request to API
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://dare2compete.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 403:
            return ResponseHelper.failure_response(
                "Dare2Compete is currently blocking requests.",
                status_code=503
            )
        
        response.raise_for_status()
        data = response.json()
        
        # Extract jobs from response
        jobs = data.get('data', {}).get('data', [])
        
        print(f"🔍 Found {len(jobs)} opportunities from Dare2Compete")
        
        results = []
        
        for job in jobs:
            try:
                # Extract description text from HTML
                details_html = job.get('details', '')
                description = ''
                if details_html:
                    soup = BeautifulSoup(details_html, 'lxml')
                    description = ' '.join(soup.stripped_strings)[:200]
                
                # Build result
                results.append({
                    'title': job.get('title', 'N/A'),
                    'company': job.get('organiser_name', 'Dare2Compete'),
                    'location': job.get('location', 'Online/Remote'),
                    'type': job.get('type', 'Internship'),
                    'description': description,
                    'link': 'https://dare2compete.com/' + str(job.get('public_url', '')),
                    'start_date': job.get('start_date', ''),
                    'end_date': job.get('end_date', ''),
                    'posted_on': job.get('display_date', 'Recently'),
                    'source': 'Dare2Compete',
                    'experience': 'Fresher'
                })
                
            except Exception as e:
                print(f"⚠️ Error parsing opportunity: {str(e)}")
                continue
        
        current_page_num = int(page) if page.isdigit() else 1
        total_pages = data.get('data', {}).get('last_page', 1)
        
        return ResponseHelper.success_response('Success scraping Dare2Compete', {
            'jobs': results,
            'pagination': {
                'current_page': current_page_num,
                'last_page': total_pages,
                'next_page': current_page_num + 1 if current_page_num < total_pages else None
            }
        })
        
    except Exception as e:
        error_msg = str(e)
        
        if "403" in error_msg or "Forbidden" in error_msg:
            return ResponseHelper.failure_response(
                "Dare2Compete is currently blocking requests.",
                status_code=503
            )
        
        if "timeout" in error_msg.lower():
            return ResponseHelper.failure_response(
                "Dare2Compete request timed out.",
                status_code=504
            )
        
        return ResponseHelper.failure_response(
            f"Error scraping Dare2Compete: {error_msg}",
            status_code=500
        )
