import re
import json
from bs4 import BeautifulSoup
from flask import jsonify
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper


def scrape_remoteok(keywords="Programmer"):
    """
    RemoteOK provides a public JSON API at https://remoteok.com/api
    This is much more reliable than web scraping
    """
    suggestions_keywords = [
        "engineer",
        "exec",
        "senior",
        "dev",
        "finance",
        "sys-admin",
        "javascript",
        "backend",
        "golang",
        "cloud",
        "medical",
        "front-end",
        "full-stack",
        "ops",
        "design",
        "react",
        "infosec",
        "marketing",
        "mobile",
        "content-writing",
        "saas",
        "recruiter",
        "full-time",
        "api",
        "sales",
        "ruby",
        "education",
        "devops",
        "stats",
        "python",
        "node",
        "english",
        "non-tech",
        "video",
        "travel",
        "quality-assurance",
        "ecommerce",
        "teaching",
        "linux",
        "java",
        "crypto",
        "junior",
        "git",
        "legal",
        "android",
        "accounting",
        "admin",
        "microsoft",
        "excel",
        "php",
        "amazon",
        "serverless",
        "css",
        "software",
        "analyst",
        "angular",
        "ios",
        "customer-support",
        "html",
        "salesforce",
        "ads",
        "product-designer",
        "hr",
        "sql",
        "c",
        "web-dev",
        "nosql",
        "postgres",
        "c-plus-plus",
        "part-time",
        "jira",
        "c-sharp",
        "seo",
        "apache",
        "data-science",
        "virtual-assistant",
        "react-native",
        "mongo",
        "testing",
        "architecture",
        "director",
        "music",
        "shopify",
        "wordpress",
        "laravel",
        "elasticsearch",
        "blockchain",
        "web3",
        "drupal",
        "docker",
        "graphql",
        "payroll",
        "internship",
        "machine-learning",
        "architect",
        "scala",
        "web",
        "objective-c",
        "social-media",
        "vue",
    ]
    # RemoteOK provides a public JSON API
    api_url = "https://remoteok.com/api"

    try:
        # Dapatkan instance cloudscraper
        scraper = CloudScraper.get_instance()

        # Kirim permintaan ke API
        response = scraper.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Filter by keyword (case insensitive)
        keyword_lower = keywords.lower()
        results = []
        
        # Skip first item (it's metadata)
        for job in data[1:]:
            try:
                # Filter by keyword in position, company, or tags
                position = job.get('position', '').lower()
                company = job.get('company', '').lower()
                tags = ' '.join(job.get('tags', [])).lower() if job.get('tags') else ''
                
                # Check if keyword matches
                if keyword_lower in position or keyword_lower in company or keyword_lower in tags:
                    results.append({
                        "title": job.get('position', 'N/A'),
                        "company_name": job.get('company', 'N/A'),
                        "location": job.get('location', 'Worldwide'),
                        "salary": job.get('salary_min', 'N/A') if job.get('salary_min') else 'N/A',
                        "company_logo": job.get('company_logo', 'N/A'),
                        "link": job.get('url', 'N/A'),
                        "description": job.get('description', '')[:200] if job.get('description') else '',
                        "date": job.get('date', ''),
                        "tags": job.get('tags', [])
                    })
                
                # Limit to 50 results
                if len(results) >= 50:
                    break
            except Exception as e:
                # Skip jobs that cause errors
                continue

        return ResponseHelper.success_response(
            "Success scraping RemoteOK jobs",
            {"jobs": results, "suggestions_keywords": suggestions_keywords},
        )

    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}")

