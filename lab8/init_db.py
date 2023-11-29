# init_db.py
from app import create_app, db, ElectroScooter
def init_database():
    app = create_app()
    with app.app_context():
        # Create the database tables
        db.create_all()
if __name__ == "__main__":
    init_database()