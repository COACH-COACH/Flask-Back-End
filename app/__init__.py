# 애플리케이션을 생성하고 설정하는 파일
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import config
import pandas as pd
import numpy as np

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    load_dotenv()

    from .views import main_view, recommendation_view, news_view
    app.register_blueprint(main_view.bp)
    app.register_blueprint(recommendation_view.recommendation)
    app.register_blueprint(news_view.news)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
    print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])

    return app

