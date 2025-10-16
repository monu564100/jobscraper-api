from bs4 import BeautifulSoup
from flask import jsonify
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper


def scrape_aasaanjobs(keyword='developer', location='bangalore', page='1'):
    """
    Scrape jobs from AasaanJobs
    
    Args:
        keyword: Search keyword (default: 'developer')
        location: City name (default: 'bangalore')
        page: Page number (default: '1')
    """
    
    # Build URL based on location
    location_slug = location.lower().replace(' ', '-')
    url = f'https://www.aasaanjobs.com/s/{location_slug}-jobs-in-{location_slug}/'
    
    try:
        # Get cloudscraper instance
        scraper = CloudScraper.get_instance()
        
        # Add headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.aasaanjobs.com/'
        }
        
        # Send request
        response = scraper.get(url, headers=headers, timeout=30)
        
        if response.status_code == 403:
            return ResponseHelper.failure_response(
                "AasaanJobs is currently blocking requests. Please try again later.",
                status_code=503
            )
        
        response.raise_for_status()
        html = response.text
        
        # Parse HTML
        page_soup = BeautifulSoup(html, 'html.parser')
        
        # Find all job containers
        containers = page_soup.find_all("div", {
            'class': 'row p-top-sm card-custom pos-relative search-highlight search-card cursor-pointer track-search-click'
        })
        
        # Try alternative selector
        if not containers:
            containers = page_soup.find_all("div", class_=lambda x: x and 'search-card' in x)
        
        print(f"🔍 Found {len(containers)} job listings from AasaanJobs")
        
        results = []
        
        for container in containers:
            try:
                # Extract Title
                title_tag = container.find("span", {'itemprop': 'title'})
                if not title_tag:
                    title_tag = container.find("h2")
                title = title_tag.text.strip().title() if title_tag else 'N/A'
                
                # Extract Apply Link
                link_tag = container.find('a')
                link = 'https://www.aasaanjobs.com' + link_tag['href'] if link_tag and link_tag.has_attr('href') else 'N/A'
                
                # Extract Description
                desc_tag = container.find("span", {'class': 'text-gray-lighter text-normal'})
                if not desc_tag:
                    desc_tag = container.find("p", class_=lambda x: x and 'text-gray' in x)
                description = desc_tag.text.strip() if desc_tag else ''
                
                # Extract Company Name
                company_tag = container.find("a", {'class': lambda x: x and 'text-primary' in x and 'track-search-click' in x})
                if not company_tag:
                    company_tag = container.find("a", class_='text-primary')
                company = company_tag.text.strip() if company_tag else 'N/A'
                
                # Extract Location
                location_tag = container.find("span", {'class': 'text-light'})
                location_text = location_tag.text.strip() if location_tag else location
                
                # Extract Experience
                qualification = container.find("div", {'class': 'col-xs-12 col-md-6 text-small text-light p-right-0'})
                experience = 'Fresher'
                if qualification:
                    exp_tag = qualification.find("span", {'class': 'm-bottom-0 text-small'})
                    if exp_tag:
                        experience = exp_tag.text.strip()
                
                # Extract Salary
                salary_tag = container.find("span", {'class': 'text-semibold'})
                salary = 'Not disclosed'
                if salary_tag:
                    salary = salary_tag.text.strip().lstrip('₹')
                
                # Extract Job Type/Skills
                skills = ''
                if qualification:
                    type_tag = qualification.find("p", {'class': 'm-bottom-0 text-small'})
                    if type_tag:
                        skills = type_tag.text.strip()
                
                # Skip if title or company is N/A
                if title == 'N/A' or company == 'N/A':
                    continue
                
                # Filter by keyword if provided
                if keyword and keyword.lower() not in title.lower() and keyword.lower() not in description.lower():
                    continue
                
                results.append({
                    'title': title,
                    'company': company,
                    'location': location_text,
                    'salary': salary,
                    'experience': experience,
                    'skills': skills,
                    'description': description[:200] if description else '',
                    'link': link,
                    'source': 'AasaanJobs',
                    'posted_on': 'Recently'
                })
                
            except Exception as e:
                print(f"⚠️ Error parsing job: {str(e)}")
                continue
        
        current_page_num = int(page) if page.isdigit() else 1
        
        return ResponseHelper.success_response('Success scraping AasaanJobs', {
            'jobs': results,
            'pagination': {
                'current_page': current_page_num,
                'last_page': current_page_num,
                'next_page': None
            }
        })
        
    except Exception as e:
        error_msg = str(e)
        
        if "403" in error_msg or "Forbidden" in error_msg:
            return ResponseHelper.failure_response(
                "AasaanJobs is currently blocking requests.",
                status_code=503
            )
        
        if "timeout" in error_msg.lower():
            return ResponseHelper.failure_response(
                "AasaanJobs request timed out.",
                status_code=504
            )
        
        return ResponseHelper.failure_response(
            f"Error scraping AasaanJobs: {error_msg}",
            status_code=500
        )
