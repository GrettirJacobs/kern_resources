from flask import Flask, jsonify
from .app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    @app.route('/test')
    def test_route():
        return jsonify({"message": "Hello from Kern Resources!"})
    
    return app