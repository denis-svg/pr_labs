# app.py
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from models.database import db
from models.electro_scooter import ElectroScooter
from flasgger import Swagger
import sys
import socket
import pickle
from main import RaftNode

def create_app(database_name, node_object):
    app = Flask(__name__)
    # Configure SQLAlchemy to use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_name}.db'
    db.init_app(app)
    # Store the loaded object in the Flask application context
    app.config['LOADED_OBJECT'] = node_object
    print(node_object)
    Swagger(app)
    return app

if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    print(sys.argv)
    if len(sys.argv) != 3:
        print("Usage: python main.py <dabase_name> <node_file>")
        sys.exit(1)

    # Extract port and node_id from command-line arguments
    database_name = sys.argv[1]
    node_file = sys.argv[2]

    with open(node_file, 'rb') as file:
        loaded_obj = pickle.load(file)
        loaded_obj.udp_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)
    print(loaded_obj.node_id, loaded_obj.follower_credentials)
    
    app = create_app(database_name, node_object=loaded_obj)
    with app.app_context():
        # Create the database tables
        db.create_all()
    import routes
    app.run(host=loaded_obj.service_info['host'], port=loaded_obj.service_info['port'])
    