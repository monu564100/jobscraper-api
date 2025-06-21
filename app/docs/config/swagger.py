from flask_restx import Api
from flask import Blueprint
from app.docs.api.glints import glints_ns
from app.docs.api.jobstreet import jobstreet_ns
from app.docs.api.indeed import indeed_ns
from app.docs.api.remoteok import remoteok_ns
from app.docs.api.disnaker import disnaker_ns

# Create blueprint for API
api_bp = Blueprint('api', __name__, url_prefix='/api/v1/')

# Initialize Flask-RESTX API
api = Api(
    api_bp,
    version='1.0',
    title='Job Scraper API',
    description='API for scraping job listings from various job portals (Glints, JobStreet, Indeed, RemoteOK, Disnaker Bandung)',
    doc='/docs/', 
    contact='ifqy gifha azhar',
    contact_email='ifqygazhar@gmail.com'
)



api.add_namespace(glints_ns, path='/api/glints')
api.add_namespace(jobstreet_ns, path='/api/jobstreet')
api.add_namespace(indeed_ns, path='/api/indeed')
api.add_namespace(remoteok_ns, path='/api/remoteok')
api.add_namespace(disnaker_ns, path='/api/disnaker')