import re
from bs4 import BeautifulSoup
from flask import jsonify
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper  

def scrape_jobs(work='Programmer', job_type='FULL_TIME', option_work='ONSITE', page='1', cookies_file='app/config/glints.json'):
    url = (
        f"https://glints.com/id/opportunities/jobs/explore?"
        f"keyword={work}+&country=ID&locationName=All+Cities/Provinces&"
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
        pagination = soup.find('div', class_='ExploreTabsc__PaginationContainer-sc-1fr7yeh-9')
        if pagination:
            last_page_button = pagination.find_all('button')[-2]  # Tombol kedua terakhir biasanya nomor halaman terakhir
            last_page = last_page_button.get_text(strip=True) if last_page_button else '1'
        else:
            last_page = '1'  # Jika tidak ada pagination, default ke 1

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

            results.append({
                'title': title,
                'salary': salary,
                'location': location,
                'link': link,
            })

        # Tambahkan informasi halaman terakhir ke dalam hasil
        return ResponseHelper.success_response('Success find job', {
            'jobs': results,
            'last_page': last_page
        })

    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}")
