# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.database import db
from models.electro_scooter import ElectroScooter
def create_app():
    app = Flask(__name__)
    # Configure SQLAlchemy to use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
    db.init_app(app)
    return app

if __name__ == "__main__":
    app = create_app()
    import routes
    app.run()