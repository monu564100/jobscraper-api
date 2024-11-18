import re
from bs4 import BeautifulSoup
from flask import jsonify
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper  

def scrape_glints(work='Programmer', job_type='FULL_TIME', option_work='ONSITE',location_id='',location_name='All+Cities/Provinces',page='1',cookies_file='app/config/glints.json'):
     # Validasi parameter
    valid_job_types = ['FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP']
    valid_work_options = ['ONSITE', 'HYBRID', 'REMOTE']
    valid_location_name = ['All+Cities/Provinces','Jabodetabek','Banten','Jawa Barat','DKI Jakarta','Jakarta Selatan, DKI Jakarta','Jakarta Barat, DKI Jakarta','Tangerang, Banten','Jakarta Utara, DKI Jakarta','Bandung, Jawa Barat']
    valid_location_id = ['','JABODETABEK','82f248c3-3fb3-4600-98fe-4afb47d7558d','06c9e480-42e7-4f11-9d6c-67ad64ccc0f6','78d63064-78a1-4577-8516-036a6c5e903e','078b37b2-e791-4739-958e-c29192e5df3e','af0ed74f-1b51-43cf-a14c-459996e39105','ae3c458e-5947-4833-8f1b-e001ce2fad1d','ea61f4ac-5864-4b2b-a2c8-aa744a2aafea','86a3dc56-1bd7-4cd3-8225-d3e4b976e552']

    if job_type not in valid_job_types:
        return ResponseHelper.failure_response(f"Invalid job_type: {job_type}. Valid options: {valid_job_types}")

    if option_work not in valid_work_options:
        return ResponseHelper.failure_response(f"Invalid option_work: {option_work}. Valid options: {valid_work_options}")

    if location_id not in valid_location_id:
        return ResponseHelper.failure_response(f"Invalid location_id: {location_id}. Valid options: {valid_location_id}") 

    if location_name not in valid_location_name:
        return ResponseHelper.failure_response(f"Invalid location_name: {location_name}. Valid options: {valid_location_name}")    

    try:
        page = int(page)
        if page <= 0:
            return ResponseHelper.failure_response("Page must be a positive integer.")
    except ValueError:
        return ResponseHelper.failure_response("Invalid page parameter. Must be an integer.")

    url = (
        f"https://glints.com/id/opportunities/jobs/explore?"
        f"keyword={work}+&country=ID&locationId={location_id}&locationName={location_name}&"
        f"lowestLocationLevel=1&jobTypes={job_type}&workArrangementOptions={option_work}&page={page}"
    )
    try:
        # Dapatkan instance cloudscraper dari CloudScraper Singleton
        scraper = CloudScraper.get_instance(cookies_file)

        # Kirim permintaan ke URL
        response = scraper.get(url)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')

          # Temukan elemen pagination
        last_page = 1  # Default ke 1 jika tidak ada pagination
        pagination = soup.find('div', class_='ExploreTabsc__PaginationContainer-sc-1fr7yeh-9')
        if pagination:
            page_buttons = pagination.find_all('button')
            if page_buttons:
                last_page_button = page_buttons[-2]  # Tombol kedua terakhir biasanya nomor halaman terakhir
                last_page = int(last_page_button.get_text(strip=True)) if last_page_button else 1

        # Parse nomor halaman terakhir menjadi integer
        last_page = int(last_page)

        # Scraping data pekerjaan
        job_cards = soup.find_all('div', {'role': 'presentation', 'aria-label': 'Job Card'})

        results = []

        for job_card in job_cards:
            # Ekstrak judul pekerjaan
            title_tag = job_card.find('h2')
            title = title_tag.get_text(strip=True) if title_tag else 'N/A'

            # Ekstrak gaji
            salary_tag = job_card.find('span', class_=re.compile(r'CompactOpportunityCardsc__SalaryWrapper'))
            salary = salary_tag.get_text(strip=True) if salary_tag else 'N/A'

            # Ekstrak lokasi
            location_tag = job_card.find('span', class_=re.compile(r'CardJobLocation__StyledTruncatedLocation'))
            location = location_tag['title'] if location_tag and location_tag.has_attr('title') else 'N/A'

            # Ekstrak link pekerjaan
            link_tag = job_card.find('a', href=True)
            link = f"https://glints.com{link_tag['href']}" if link_tag else 'N/A'

             # Ekstrak nama perusahaan
            company_name_tag = job_card.find('a', class_=re.compile(r'CompactOpportunityCardsc__CompanyLink'))
            company_name = company_name_tag.get_text(strip=True) if company_name_tag else 'N/A'

            # Ekstrak logo perusahaan
            company_logo_tag = job_card.find('img', class_=re.compile(r'CompactOpportunityCardsc__CompanyAvatar'))
            company_logo = company_logo_tag['src'] if company_logo_tag and company_logo_tag.has_attr('src') else 'N/A'

            results.append({
                'title': title,
                'salary': salary,
                'location': location,
                'company_name': company_name,
                'company_logo': company_logo,
                'link': link,
            })

        # Tambahkan informasi halaman terakhir ke dalam hasil
        return ResponseHelper.success_response('Success find job', {
            'jobs': results,
            'last_page': last_page
        })

    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}")
