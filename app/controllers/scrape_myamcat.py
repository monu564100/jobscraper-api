import requests
from bs4 import BeautifulSoup
from app.helpers.response import ResponseHelper


def scrape_myamcat(start_limit='117', max_pages=3):
    """
    Scrape jobs from MyAmcat (uses their AJAX API)
    """
    
    try:
        results = []
        
        for i in range(int(start_limit), int(start_limit) + max_pages):
            url = f'https://www.myamcat.com/jobs-search-ajax?strEventID=1&strCompanyID=&strMinSalary=0&strMaxSalary=9900000&strStartLimit=0&strKeyword=&strAdvCategoryName=0&strAdvLocationID=0&strAdvSectorID=&strAdvFlagID=0&sortBy=2&strJobRolesList=&strCompaniesList=&strInvitedJobs=0&strFreeSearchText=0&strHeaderJobSearchLocation=&_=1524471212{i}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.myamcat.com/jobs'
            }
            
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                jobs = data.get('1', [])
                
                for job in jobs:
                    try:
                        # Extract description
                        desc_html = job.get('description', '')
                        soup = BeautifulSoup(desc_html, 'lxml')
                        description = ' '.join(soup.stripped_strings).replace('\xa0', ' ')
                        
                        # Build link
                        jd_link = job.get('jdLink', '')
                        link = 'https://www.myamcat.com' + jd_link if jd_link else 'N/A'
                        
                        # Min job experience
                        min_exp = job.get('minJobEx', 0)
                        experience = f"{min_exp} yrs" if min_exp else 'Fresher'
                        
                        results.append({
                            'title': job.get('jobprofileName', 'N/A'),
                            'company': job.get('companyName', 'N/A'),
                            'location': job.get('cityName', 'India'),
                            'salary': job.get('salary', 'Not disclosed'),
                            'experience': experience,
                            'description': description[:200] if description else '',
                            'link': link,
                            'posted_on': job.get('datePosted', 'Recently'),
                            'source': 'MyAmcat'
                        })
                        
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"⚠️ Error fetching page {i}: {str(e)}")
                continue
        
        print(f"🔍 Found {len(results)} jobs from MyAmcat")
        
        return ResponseHelper.success_response('Success scraping MyAmcat', {
            'jobs': results,
            'pagination': {'current_page': 1, 'last_page': 1, 'next_page': None}
        })
        
    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}", status_code=500)
