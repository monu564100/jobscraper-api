from flask import Flask
from app.routes.scrape_glints_route import scraper_bp

def create_app():
    app = Flask(__name__)
    
    # Registrasi Blueprints
    app.register_blueprint(scraper_bp, url_prefix='/api')
    
    return app