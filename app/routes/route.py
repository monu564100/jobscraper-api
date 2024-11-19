from flask import Blueprint, request
from app.controllers.scrape_glints import scrape_glints
from app.controllers.scrape_jobstreet import scrape_jobstreet
from app.controllers.scrape_remoteok import scrape_remoteok

scraper_bp = Blueprint('scraper', __name__)

@scraper_bp.route('/glints', methods=['GET'])
def scrape():
    try:
        # Mendapatkan parameter dari query string dengan default values
        work = request.args.get('work', 'Programmer')
        job_type = request.args.get('job_type', 'FULL_TIME')
        option_work = request.args.get('option_work', 'ONSITE')
        page = request.args.get('page', '1')
        location_id = request.args.get('location_id', '')  # Default kosong
        location_name = request.args.get('location_name', 'All+Cities/Provinces')

        # Panggil fungsi scraping dengan parameter
        return scrape_glints(work, job_type, option_work, location_id, location_name, page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500

@scraper_bp.route('/jobstreet', methods=['GET'])
def scrape_jobstreet_route():
    try:
        work = request.args.get('work', 'Programmer')
        location = request.args.get('location', 'Jakarta Raya')
        country = request.args.get('country','id')
        page = request.args.get('page','1')


        return scrape_jobstreet(work,location,country,page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500

@scraper_bp.route('/remoteok',methods=['GET'])
def scrape_remoteok_route():  
    try:
        keywords = request.args.get('keywords','python')

        return scrape_remoteok(keywords)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500