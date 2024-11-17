# app/routes/scraper_routes.py

from flask import Blueprint, request
from app.controllers.scrape_glints import scrape_jobs

scraper_bp = Blueprint('scraper', __name__)

@scraper_bp.route('/glints', methods=['GET'])
def scrape():
    # Mendapatkan parameter dari query string dengan default values
    work = request.args.get('work', 'Programmer')
    job_type = request.args.get('job_type', 'FULL_TIME')
    option_work = request.args.get('option_work', 'ONSITE')
    page = request.args.get('page','1')

    # Panggil fungsi scraping
    return scrape_jobs(work, job_type, option_work,page)
