# web_interface/app.py
from flask import Flask
from .routes import main_bp
from config import Config  # Import Config here

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(main_bp)
