from flask import Blueprint, request
from app.controllers.scrape_glints import scrape_glints
from app.controllers.scrape_jobstreet import scrape_jobstreet
from app.controllers.scrape_remoteok import scrape_remoteok
from app.controllers.scrape_indeed import scrape_indeed
from app.controllers.scrape_disnaker_bandung import scrape_disnaker_bandung
from app.controllers.scrape_internshala import scrape_internshala
from app.controllers.scrape_aasaanjobs import scrape_aasaanjobs
from app.controllers.scrape_dare2compete import scrape_dare2compete
from app.controllers.scrape_freshersworld import scrape_freshersworld
from app.controllers.scrape_jobguru import scrape_jobguru
from app.controllers.scrape_timesjobs import scrape_timesjobs
from app.controllers.scrape_myamcat import scrape_myamcat
from app.controllers.scrape_linkedin import scrape_linkedin
from app.controllers.aggregate_jobs import get_aggregate_jobs
from app.controllers.jobspy_proxy import jobspy_search
from app.controllers.scrape_naukri import scrape_naukri
from app.controllers.scrape_ziprecruiter import scrape_ziprecruiter

scraper_bp = Blueprint("scraper", __name__)


@scraper_bp.route("/glints", methods=["GET"])
def scrape():
    try:
        # Mendapatkan parameter dari query string dengan default values
        work = request.args.get("work", "Programmer")
        job_type = request.args.get("job_type", "FULL_TIME")
        option_work = request.args.get("option_work", "ONSITE")
        page = request.args.get("page", "1")
        location_id = request.args.get("location_id", "")  # Default kosong
        location_name = request.args.get("location_name", "All+Cities/Provinces")

        # Panggil fungsi scraping dengan parameter
        return scrape_glints(
            work, job_type, option_work, location_id, location_name, page
        )
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/jobstreet", methods=["GET"])
def scrape_jobstreet_route():
    try:
        work = request.args.get("work", "Programmer")
        location = request.args.get("location", "Jakarta Raya")
        country = request.args.get("country", "id")
        page = request.args.get("page", "1")

        return scrape_jobstreet(work, location, country, page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/remoteok", methods=["GET"])
def scrape_remoteok_route():
    try:
        keywords = request.args.get("keywords", "python")

        return scrape_remoteok(keywords)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/indeed", methods=["GET"])
def scrape_indeed_route():
    try:
        keyword = request.args.get("keyword", "programmer")
        location = request.args.get("location", "")
        country = request.args.get("country", "id")
        page = request.args.get("page", "0")

        return scrape_indeed(keyword, location, country, page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/disnaker_bandung", methods=["GET"])
def scrape_disnaker_bandung_route():
    try:
        page = request.args.get("page", "1")
        return scrape_disnaker_bandung(page)

    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/internshala", methods=["GET"])
def scrape_internshala_route():
    try:
        keyword = request.args.get("keyword", "developer")
        location = request.args.get("location", "bangalore")
        page = request.args.get("page", "1")

        return scrape_internshala(keyword, location, page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/aasaanjobs", methods=["GET"])
def scrape_aasaanjobs_route():
    try:
        keyword = request.args.get("keyword", "developer")
        location = request.args.get("location", "bangalore")
        page = request.args.get("page", "1")

        return scrape_aasaanjobs(keyword, location, page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/dare2compete", methods=["GET"])
def scrape_dare2compete_route():
    try:
        opportunity_type = request.args.get("type", "internships")
        page = request.args.get("page", "1")

        return scrape_dare2compete(opportunity_type, page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/freshersworld", methods=["GET"])
def scrape_freshersworld_route():
    try:
        keyword = request.args.get("keyword", "")
        location = request.args.get("location", "bangalore")
        limit = request.args.get("limit", "50")

        return scrape_freshersworld(keyword, location, limit)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/jobguru", methods=["GET"])
def scrape_jobguru_route():
    try:
        return scrape_jobguru()
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/timesjobs", methods=["GET"])
def scrape_timesjobs_route():
    try:
        location = request.args.get("location", "bangalore")
        limit = request.args.get("limit", "50")

        return scrape_timesjobs(location, limit)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/myamcat", methods=["GET"])
def scrape_myamcat_route():
    try:
        start_limit = request.args.get("start", "117")
        max_pages = request.args.get("pages", "3")

        return scrape_myamcat(start_limit, int(max_pages))
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/linkedin", methods=["GET"])
def scrape_linkedin_route():
    """
    LinkedIn job scraper endpoint (placeholder)
    GET /api/linkedin?keyword=developer&location=bangalore&limit=25
    """
    try:
        keyword = request.args.get("keyword", "developer")
        location = request.args.get("location", "")
        limit = request.args.get("limit", "25")

        return scrape_linkedin(keyword, location, int(limit))
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/aggregate", methods=["GET"])
def aggregate_jobs_route():
    """
    Job aggregator endpoint - Fetches from ALL sources and returns top 20 filtered jobs
    GET /api/aggregate?keyword=developer&location=bangalore&jobTitle=python developer
    
    This endpoint:
    - Fetches jobs from all 9 sources concurrently
    - Analyzes and scores each job based on recency, location match, title match
    - Returns top 20 best matching jobs
    - Ensures diversity (at least 2 from each working source)
    """
    return get_aggregate_jobs()

@scraper_bp.route("/jobspy", methods=["GET"])
def jobspy_route():
    try:
        return jobspy_search()
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500

@scraper_bp.route("/naukri", methods=["GET"])
def scrape_naukri_route():
    try:
        keyword = request.args.get("keyword", "developer")
        location = request.args.get("location", "")
        limit = int(request.args.get("limit", "20"))
        return scrape_naukri(keyword, location, limit)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500

@scraper_bp.route("/ziprecruiter", methods=["GET"])
def scrape_ziprecruiter_route():
    try:
        search_term = request.args.get("search_term", request.args.get("keyword", ""))
        location = request.args.get("location", "")
        distance = int(request.args.get("distance", "50"))
        job_type = request.args.get("job_type", "")
        is_remote = request.args.get("is_remote") == 'true'
        hours_old = int(request.args.get("hours_old", "96"))
        page = int(request.args.get("page", "1"))
        return scrape_ziprecruiter(search_term, location, distance, job_type, is_remote, hours_old, page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500

