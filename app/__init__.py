from flask import Flask
from flask_cors import CORS
from app.routes.route import scraper_bp

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["*"])
    
    # Registrasi Blueprints
    app.register_blueprint(scraper_bp, url_prefix='/api')
    
    return app