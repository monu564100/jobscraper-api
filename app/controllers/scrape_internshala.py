import re
from bs4 import BeautifulSoup
from flask import jsonify
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper


def scrape_internshala(keyword='developer', location='bangalore', page='1'):
    """
    Scrape internships from Internshala
    
    Args:
        keyword: Search keyword (e.g., 'developer', 'python', 'design')
        location: City name (e.g., 'bangalore', 'delhi', 'mumbai')
        page: Page number (default 1)
    """
    
    # Build URL based on keyword and location
    if keyword.lower() == 'all' or not keyword:
        # All internships in location
        url = f'https://internshala.com/internships/internship-in-{location.lower()}/page-{page}'
    else:
        # Search by keyword and location
        url = f'https://internshala.com/internships/{keyword.lower()}-internship-in-{location.lower()}/page-{page}'
    
    try:
        # Get cloudscraper instance
        scraper = CloudScraper.get_instance()
        
        # Add better headers to bypass blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://internshala.com/'
        }
        
        # Send request
        response = scraper.get(url, headers=headers, timeout=30)
        
        # Check for blocking
        if response.status_code == 403:
            return ResponseHelper.failure_response(
                "Internshala is currently blocking requests. Please try again later.",
                status_code=503
            )
        
        response.raise_for_status()
        html = response.text
        
        # Parse HTML
        page_soup = BeautifulSoup(html, 'html.parser')
        
        # Find all internship containers - try multiple selectors
        containers = page_soup.find_all("div", {"class": "container-fluid individual_internship"})
        
        # Try alternative selector if first one fails
        if not containers:
            containers = page_soup.find_all("div", {"class": re.compile(r"individual_internship")})
        
        # Try another alternative selector
        if not containers:
            containers = page_soup.find_all("div", {"class": "internship_meta"})
        
        print(f"🔍 Found {len(containers)} internship listings from Internshala")
        
        results = []
        
        for container in containers:
            try:
                # Extract Title and Link
                title_tag = container.find('h3', class_='profile')
                if not title_tag:
                    title_tag = container.find('a', class_=re.compile(r'view_detail'))
                if not title_tag:
                    title_tag = container.find('h3')
                if not title_tag:
                    title_tag = container.find('a', class_='profile')
                
                title = title_tag.get_text(strip=True) if title_tag else 'N/A'
                
                # Extract Apply Link - try multiple approaches
                apply_link = 'N/A'
                
                # Method 1: From title tag
                if title_tag and title_tag.has_attr('href'):
                    apply_link = 'https://internshala.com' + title_tag['href']
                
                # Method 2: Find any link in container with 'detail' in href
                if apply_link == 'N/A':
                    link_tag = container.find('a', href=re.compile(r'/internship/detail/'))
                    if link_tag and link_tag.has_attr('href'):
                        apply_link = 'https://internshala.com' + link_tag['href']
                
                # Method 3: Find the view details button
                if apply_link == 'N/A':
                    detail_btn = container.find('div', class_='view_detail_button')
                    if detail_btn:
                        parent_link = detail_btn.find_parent('a')
                        if parent_link and parent_link.has_attr('href'):
                            apply_link = 'https://internshala.com' + parent_link['href']
                
                # Extract Company Name
                company_tag = container.find('a', class_='link_display_like_text')
                if not company_tag:
                    company_tag = container.find('p', class_='company-name')
                company = company_tag.get_text(strip=True) if company_tag else 'N/A'
                
                # Extract Location
                location_tag = container.find('a', class_='location_link')
                if not location_tag:
                    location_tag = container.find('span', class_='location')
                if not location_tag:
                    location_tag = container.find('div', id=re.compile(r'location'))
                location_text = location_tag.get_text(strip=True) if location_tag else location
                
                # Extract Stipend/Salary
                stipend_tag = container.find('span', class_='stipend')
                if not stipend_tag:
                    stipend_tag = container.find('td', class_='stipend_container_table_cell')
                if not stipend_tag:
                    stipend_tag = container.find('div', class_='item_body')
                stipend = stipend_tag.get_text(strip=True) if stipend_tag else 'Unpaid'
                
                # Extract Type (Full-time, Part-time, Work from home)
                type_tag = container.find('div', class_='button_container')
                if type_tag:
                    type_inner = type_tag.find('div')
                    internship_type = type_inner.get_text(strip=True) if type_inner else 'N/A'
                else:
                    # Check for work from home tag
                    wfh_tag = container.find('span', class_=re.compile(r'work_from_home'))
                    internship_type = 'Work from home' if wfh_tag else 'In-office'
                
                # Extract Start Date
                start_tag = container.find('div', id='start-date-first')
                if not start_tag:
                    start_tag = container.find('span', class_='start-date')
                start_date = start_tag.get_text(strip=True) if start_tag else 'Immediately'
                
                # Extract Apply By (End Date)
                apply_by = 'N/A'
                table = container.find('div', class_='table-responsive')
                if table:
                    cells = table.find_all('td')
                    if len(cells) >= 5:
                        apply_by = cells[4].get_text(strip=True)
                
                # Extract Posted On (Created Date)
                posted_on = 'Recently'
                if table:
                    cells = table.find_all('td')
                    if len(cells) >= 4:
                        posted_on = cells[3].get_text(strip=True)
                
                # Extract Duration
                duration = 'N/A'
                duration_tag = container.find('div', class_='item_body')
                if duration_tag:
                    duration_text = duration_tag.get_text(strip=True)
                    if 'month' in duration_text.lower() or 'week' in duration_text.lower():
                        duration = duration_text
                
                # Skip if title or company is N/A
                if title == 'N/A' or company == 'N/A':
                    continue
                
                # If no direct link, create a search link as fallback
                if apply_link == 'N/A' or not apply_link or apply_link == '':
                    # Create a search URL with company name and title
                    search_query = f"{title} {company}".replace(' ', '+')
                    apply_link = f"https://internshala.com/internships/keywords-{search_query}"
                
                results.append({
                    'title': title,
                    'company': company,
                    'location': location_text,
                    'salary': stipend,
                    'type': internship_type,
                    'start_date': start_date,
                    'apply_by': apply_by,
                    'posted_on': posted_on,
                    'duration': duration,
                    'link': apply_link,
                    'source': 'Internshala',
                    'experience': 'Fresher'
                })
                
            except Exception as e:
                # Skip jobs that cause errors
                print(f"⚠️ Error parsing internship: {str(e)}")
                continue
        
        # Calculate pagination
        current_page_num = int(page) if page.isdigit() else 1
        
        # Try to find pagination info
        pagination_container = page_soup.find('div', id='pagination')
        last_page = current_page_num
        
        if pagination_container:
            page_links = pagination_container.find_all('a')
            page_numbers = []
            for link in page_links:
                try:
                    page_num = int(link.get_text(strip=True))
                    page_numbers.append(page_num)
                except:
                    continue
            if page_numbers:
                last_page = max(page_numbers)
        
        next_page = current_page_num + 1 if current_page_num < last_page else None
        
        return ResponseHelper.success_response('Success scraping Internshala internships', {
            'jobs': results,
            'pagination': {
                'current_page': current_page_num,
                'last_page': last_page,
                'next_page': next_page
            }
        })
        
    except Exception as e:
        error_msg = str(e)
        
        # Check if it's a 403 blocking error
        if "403" in error_msg or "Forbidden" in error_msg:
            return ResponseHelper.failure_response(
                "Internshala is currently blocking requests. Please try other sources.",
                status_code=503
            )
        
        # Check if it's a timeout
        if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            return ResponseHelper.failure_response(
                "Internshala request timed out. Please try again.",
                status_code=504
            )
        
        # General error
        return ResponseHelper.failure_response(
            f"Error scraping Internshala: {error_msg}",
            status_code=500
        )
