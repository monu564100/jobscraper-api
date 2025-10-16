"""
LinkedIn Job Scraper Controller
Full Selenium-based implementation
"""

from flask import jsonify
from app.providers.linkedin_scraper import scrape_linkedin_route


def scrape_linkedin(keyword, location='', limit=25):
    """
    Scrape LinkedIn jobs using Selenium
    
    Args:
        keyword: Job title or keywords
        location: Location (city, country)
        limit: Maximum number of results (default: 25)
    
    Returns:
        JSON response with jobs data
    """
    
    try:
        # Call the scraper
        result = scrape_linkedin_route(keyword, location, filters=None, limit=int(limit))
        
        if result['status'] == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 503
        
    except Exception as e:
        return jsonify({
            "status": "failed",
            "message": f"LinkedIn scraping error: {str(e)}",
            "data": {"jobs": []}
        }), 500
