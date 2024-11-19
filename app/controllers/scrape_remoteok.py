import re
import json
from bs4 import BeautifulSoup
from flask import jsonify
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper

def scrape_remoteok(keywords='Programmer'):
    suggestions_keywords = [
        'engineer', 'exec', 'senior', 'dev', 'finance', 'sys-admin', 
        'javascript', 'backend', 'golang', 'cloud', 'medical', 'front-end', 
        'full-stack', 'ops', 'design', 'react', 'infosec', 'marketing', 
        'mobile', 'content-writing', 'saas', 'recruiter', 'full-time', 
        'api', 'sales', 'ruby', 'education', 'devops', 'stats', 'python', 
        'node', 'english', 'non-tech', 'video', 'travel', 'quality-assurance', 
        'ecommerce', 'teaching', 'linux', 'java', 'crypto', 'junior', 'git', 
        'legal', 'android', 'accounting', 'admin', 'microsoft', 'excel', 
        'php', 'amazon', 'serverless', 'css', 'software', 'analyst', 'angular', 
        'ios', 'customer-support', 'html', 'salesforce', 'ads', 'product-designer', 
        'hr', 'sql', 'c', 'web-dev', 'nosql', 'postgres', 'c-plus-plus', 
        'part-time', 'jira', 'c-sharp', 'seo', 'apache', 'data-science', 
        'virtual-assistant', 'react-native', 'mongo', 'testing', 'architecture', 
        'director', 'music', 'shopify', 'wordpress', 'laravel', 'elasticsearch', 
        'blockchain', 'web3', 'drupal', 'docker', 'graphql', 'payroll', 
        'internship', 'machine-learning', 'architect', 'scala', 'web', 
        'objective-c', 'social-media', 'vue'
    ]
    base_url = f"https://remoteok.com/remote-{keywords}-jobs?location=Worldwide"
    
    try:
        # Dapatkan instance cloudscraper
        scraper = CloudScraper.get_instance()
        
        # Kirim permintaan ke URL
        response = scraper.get(base_url)
        response.raise_for_status()
        html = response.text

        # Parsing HTML menggunakan BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Dapatkan semua elemen <tr> pekerjaan
        job_rows = soup.find_all('tr', class_=re.compile(r'job.*'))
        results = []

        for row in job_rows:
            # Periksa jika elemen memiliki class "closed"
            if "closed" in row.get('class', []):
                continue  # Lewati elemen yang "closed"

            # Ekstrak informasi pekerjaan
            job_title_tag = row.find('h2', itemprop='title')
            company_tag = row.find('h3', itemprop='name')
            location_tag = row.find('div', class_='location')
            salary_tag = row.find('div', text=re.compile(r'\$'))
            link_tag = row.get('data-href')

            # Ekstrak logo dari elemen <script> JSON
            logo_url = None
            logo_script_tag = row.find('script', type='application/ld+json')
            if logo_script_tag:
                try:
                    logo_data = json.loads(logo_script_tag.string)
                    logo_url = logo_data.get("image", None)
                except json.JSONDecodeError:
                    logo_url = None

            # Tambahkan informasi ke hasil
            results.append({
                'title': job_title_tag.get_text(strip=True) if job_title_tag else 'N/A',
                'company': company_tag.get_text(strip=True) if company_tag else 'N/A',
                'location': location_tag.get_text(strip=True) if location_tag else 'Worldwide',
                'salary': salary_tag.get_text(strip=True) if salary_tag else 'N/A',
                'logo': logo_url if logo_url else 'N/A',
                'job_url': f"https://remoteok.com{link_tag}" if link_tag else 'N/A'
            })

        return ResponseHelper.success_response('Success scraping RemoteOK jobs', {
            'jobs': results,
            'suggestions_keywords': suggestions_keywords
        })

    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}")