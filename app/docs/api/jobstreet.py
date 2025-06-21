from flask_restx import Namespace, Resource, fields
from flask import request
from app.controllers.scrape_jobstreet import scrape_jobstreet

jobstreet_ns = Namespace('jobstreet', description='JobStreet job scraping operations')

# Models untuk dokumentasi...
@jobstreet_ns.route('')
class JobStreetAPI(Resource):
    @jobstreet_ns.doc('scrape_jobstreet_jobs')
    @jobstreet_ns.param('work', 'Job keyword to search for', default='Programmer')
    @jobstreet_ns.param('location', 'Job location', default='Jakarta Raya')
    @jobstreet_ns.param('country', 'Country code', enum=['id', 'my', 'sg', 'th', 'hk', 'nz', 'au'], default='id')
    @jobstreet_ns.param('page', 'Page number', type=int, default=1)
    def get(self):
        """Scrape jobs from JobStreet"""
        work = request.args.get('work', 'Programmer')
        location = request.args.get('location', 'Jakarta Raya')
        country = request.args.get('country', 'id')
        page = request.args.get('page', 1)
        
        return scrape_jobstreet(work, location, country, page)