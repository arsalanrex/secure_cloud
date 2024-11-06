# web_interface/app.py
from flask import Flask
from .routes import main_bp

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(main_bp)