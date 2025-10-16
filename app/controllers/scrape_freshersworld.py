from bs4 import BeautifulSoup
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper


def scrape_freshersworld(keyword='', location='bangalore', limit='50'):
    """
    Scrape jobs from FreshersWorld
    """
    
    url = f'https://www.freshersworld.com/jobs/jobsearch?txt={keyword}&limit={limit}'
    
    try:
        scraper = CloudScraper.get_instance()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.freshersworld.com/'
        }
        
        response = scraper.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        page_soup = BeautifulSoup(response.text, 'html.parser')
        
        containers = page_soup.find_all("div", {
            "class": "col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space"
        })
        
        if not containers:
            containers = page_soup.find_all("div", class_=lambda x: x and 'job-container' in x)
        
        print(f"🔍 Found {len(containers)} jobs from FreshersWorld")
        
        results = []
        
        for container in containers:
            try:
                # Title
                job_role = container.find("div", class_="job-title")
                if not job_role:
                    job_divs = container.find_all("div")
                    if len(job_divs) > 4:
                        job_role = job_divs[4]
                title = job_role.text.strip().title() if job_role else 'N/A'
                
                # Apply Link
                link_tag = container.find('a')
                link = link_tag['href'] if link_tag and link_tag.has_attr('href') else 'N/A'
                
                # Description
                desc_tag = container.find("span", {"class": "desc"})
                description = desc_tag.text.strip().replace('\xa0', ' ') if desc_tag else ''
                
                # Company
                company_tag = container.find('h3')
                company = company_tag.text.strip() if company_tag else 'N/A'
                
                # Location
                location_tag = container.find("span", {"class": "job-location display-block modal-open"})
                if not location_tag:
                    location_tag = container.find("span", class_=lambda x: x and 'job-location' in x)
                location_text = location_tag.text.strip() if location_tag else location
                
                # Skills/Qualification
                qual_tag = container.find("span", {"itemprop": "qualifications"})
                skills = qual_tag.text.strip() if qual_tag else ''
                
                # End Date
                date_tag = container.find("span", {"itemprop": "datePosted"})
                end_date = date_tag.text.strip() if date_tag else ''
                
                # Posted On
                ago_tag = container.find("span", {"class": "ago-text"})
                posted_on = ago_tag.text.strip() if ago_tag else 'Recently'
                
                if title == 'N/A' or company == 'N/A':
                    continue
                
                results.append({
                    'title': title,
                    'company': company,
                    'location': location_text,
                    'skills': skills,
                    'description': description[:200] if description else '',
                    'link': link,
                    'end_date': end_date,
                    'posted_on': posted_on,
                    'source': 'FreshersWorld',
                    'experience': 'Fresher'
                })
                
            except Exception as e:
                continue
        
        return ResponseHelper.success_response('Success scraping FreshersWorld', {
            'jobs': results,
            'pagination': {'current_page': 1, 'last_page': 1, 'next_page': None}
        })
        
    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}", status_code=500)
