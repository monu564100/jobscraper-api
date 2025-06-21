from flask_restx import Namespace, Resource, fields
from flask import request
from app.controllers.scrape_indeed import scrape_indeed

indeed_ns = Namespace('indeed', description='Indeed job scraping operations')

@indeed_ns.route('')
class IndeedAPI(Resource):
    @indeed_ns.doc('scrape_indeed_jobs')
    @indeed_ns.param('keyword', 'Job keyword to search for', default='programmer')
    @indeed_ns.param('location', 'Job location', default='')
    @indeed_ns.param('country', 'Country code', default='id')
    @indeed_ns.param('page', 'Page start value', default='0')
    def get(self):
        """Scrape jobs from Indeed"""
        keyword = request.args.get('keyword', 'programmer')
        location = request.args.get('location', '')
        country = request.args.get('country', 'id')
        page = request.args.get('page', '0')
        
        return scrape_indeed(keyword, location, country, page)