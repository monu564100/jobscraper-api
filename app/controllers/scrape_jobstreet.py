import re
from bs4 import BeautifulSoup
from flask import jsonify
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper

def scrape_jobstreet(work='Programmer', location='', country="id",page=1, cookies_file='app/config/jobstreet.json'):
    country_urls = {
        "id": "https://id.jobstreet.com/id/{work}-jobs/in-{location}?page={page}",
        "my": "https://my.jobstreet.com/{work}-jobs/in-{location}?page={page}",
        "sg": "https://sg.jobstreet.com/{work}-jobs/in-{location}?page={page}",
        "th": "https://th.jobsdb.com/th/{work}-jobs/in-{location}?page={page}",
        "hk": "https://hk.jobsdb.com/{work}-jobs/in-{location}?page={page}",
        "nz": "https://www.seek.co.nz/{work}-jobs/in-{location}?page={page}",
        "au": "https://www.seek.com.au/{work}-jobs/in-{location}?page={page}",
    }


    if country not in country_urls:
        country = "id"  
    url = country_urls[country].format(work=work, location=location, page=page)

    try:
        scraper = CloudScraper.get_instance()
        
        # Kirim permintaan ke URL
        response = scraper.get(url)
        response.raise_for_status()
        html = response.text

        # Parsing HTML menggunakan BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Dapatkan total hasil pencarian
        total_jobs_tag = soup.find('h1', id="SearchSummary", attrs={"data-automation": "totalJobsMessage"})
        total_jobs = total_jobs_tag.find('span', attrs={"data-automation": "totalJobsCount"}).get_text(strip=True) if total_jobs_tag else '0'
        
        # Dapatkan elemen job card
        job_cards = soup.find_all('article', attrs={"data-automation": "normalJob"})
        
        results = []
        for job_card in job_cards:
            # Ekstrak judul pekerjaan
            title_tag = job_card.find('a', attrs={"data-automation": "jobTitle"})
            title = title_tag.get_text(strip=True) if title_tag else 'N/A'

            # Ekstrak nama perusahaan
            company_name_tag = job_card.find('a', attrs={"data-automation": "jobCompany"})
            company_name = company_name_tag.get_text(strip=True) if company_name_tag else 'N/A'

            # Ekstrak logo perusahaan
            company_logo_container = job_card.find('div', attrs={"data-automation": "company-logo-container"})
            company_logo_tag = company_logo_container.find('img') if company_logo_container else None
            company_logo = company_logo_tag['src'] if company_logo_tag and company_logo_tag.has_attr('src') else 'N/A'

            # Ekstrak gaji
            salary_tag = job_card.find('span', attrs={"data-automation": "jobSalary"})
            salary = salary_tag.get_text(strip=True) if salary_tag else 'N/A'

            # Ekstrak lokasi
            location_tags = job_card.find_all('a', attrs={"data-automation": "jobLocation"})
            location = ', '.join([tag.get_text(strip=True) for tag in location_tags]) if location_tags else 'N/A'

            # Ekstrak link pekerjaan
            link_tag = job_card.find('a', href=True, attrs={"data-automation": "jobTitle"})
            link = f"https://{country_urls[country].split('/')[2]}{link_tag['href']}" if link_tag else 'N/A'

            results.append({
                'title': title,
                'company_name': company_name,
                'company_logo': company_logo,
                'salary': salary,
                'location': location,
                'link': link,
            })
        
        # Scrape pagination
        pagination = soup.find('ul', class_='_1ungv2r0 _1ungv2r3 _1viagsn5b _1viagsngv')
        current_page = page
        last_page = 1  # Default to 1 if no pagination found
        has_next = False
        if pagination:
            # Ambil nomor halaman tertinggi
            page_tags = pagination.find_all('a', attrs={"data-automation": re.compile(r"page-\d+")})
            if page_tags:
                last_page_numbers = [
                    int(tag.get_text(strip=True)) for tag in page_tags if tag.get_text(strip=True).isdigit()
                ]
                last_page = max(last_page_numbers, default=1)

            # Periksa jika elemen "Next" ada
            next_button = pagination.find('a', rel="nofollow next")
            has_next = next_button is not None

        # Scrape suggestion location
        suggestion_span = soup.find('span', class_='_1ungv2r0 _1viagsn4z _1viagsnr')
        suggestion_location = []
        if suggestion_span:
            suggestion_links = suggestion_span.find_all('a', attrs={"data-automation": re.compile(r"didYouMeanLocation\d+")})
            for link in suggestion_links:
                suggestion_location.append({
                    'location_name': link.get_text(strip=True),
                    'url': f"https://{country_urls[country].split('/')[2]}{link['href']}" if link.has_attr('href') else 'N/A'
                })

        return ResponseHelper.success_response('Success find job', {
            'total_jobs': total_jobs,
            'jobs': results,
            'pagination': {
                'current_page': current_page,
                'last_page': last_page,
                'has_next': has_next
            },
            'suggestion_location': suggestion_location
        })

    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}")
