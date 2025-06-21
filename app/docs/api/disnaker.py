from flask_restx import Namespace, Resource, fields
from flask import request
from app.controllers.scrape_disnaker_bandung import scrape_disnaker_bandung

disnaker_ns = Namespace('disnaker', description='Disnaker Bandung job scraping operations')

@disnaker_ns.route('')
class DisnakerAPI(Resource):
    @disnaker_ns.doc('scrape_disnaker_jobs')
    @disnaker_ns.param('page', 'Page number', type=int, default=1)
    def get(self):
        """Scrape jobs from Disnaker Bandung"""
        page = request.args.get('page', '1')
        
        return scrape_disnaker_bandung(page)