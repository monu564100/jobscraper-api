from flask_restx import Namespace, Resource, fields
from flask import request
from app.controllers.scrape_glints import scrape_glints

glints_ns = Namespace('glints', description='Glints job scraping operations')

# Models tetap sama untuk dokumentasi...
job_model = glints_ns.model('GlintsJob', {
    'title': fields.String(description='Job title', example='Software Engineer'),
    'salary': fields.String(description='Job salary', example='Rp 8,000,000 - Rp 12,000,000'),
    'location': fields.String(description='Job location', example='Jakarta, Indonesia'),
    'company_name': fields.String(description='Company name', example='Tech Company'),
    'company_logo': fields.String(description='Company logo URL'),
    'link': fields.String(description='Job link')
})

glints_data_model = glints_ns.model('GlintsData', {
    'jobs': fields.List(fields.Nested(job_model)),
    'last_page': fields.Integer(description='Last page number', example=25)
})

success_response_model = glints_ns.model('GlintsSuccessResponse', {
    'status': fields.String(description='Response status', example='success'),
    'message': fields.String(description='Response message', example='Success find job'),
    'data': fields.Nested(glints_data_model)
})

@glints_ns.route('')
class GlintsAPI(Resource):
    @glints_ns.doc('scrape_glints_jobs')
    @glints_ns.param('work', 'Job keyword to search for', default='Programmer')
    @glints_ns.param('job_type', 'Type of job', enum=['FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP'], default='FULL_TIME')
    @glints_ns.param('option_work', 'Work arrangement option', enum=['ONSITE', 'HYBRID', 'REMOTE'], default='ONSITE')
    @glints_ns.param('location_id', 'Location ID', default='')
    @glints_ns.param('location_name', 'Location name', default='All+Cities/Provinces')
    @glints_ns.param('page', 'Page number', type=int, default=1)
    @glints_ns.response(200, 'Success', success_response_model)
    def get(self):
        """Scrape jobs from Glints Indonesia"""
        work = request.args.get('work', 'Programmer')
        job_type = request.args.get('job_type', 'FULL_TIME')
        option_work = request.args.get('option_work', 'ONSITE')
        location_id = request.args.get('location_id', '')
        location_name = request.args.get('location_name', 'All+Cities/Provinces')
        page = request.args.get('page', '1')
        
        # Langsung panggil controller asli
        return scrape_glints(work, job_type, option_work, location_id, location_name, page)