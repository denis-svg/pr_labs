# Import necessary modules
from flask import request, jsonify
from models.database import db
from models.electro_scooter import ElectroScooter
from __main__ import app


@app.route('/api/electro-scooters', methods=['POST'])
def create_electro_scooter():
    try:
        # Get data from the request body
        data = request.get_json()
        # Validate and extract required parameters
        name = data['name']
        battery_level = data['battery_level']
        # Create a new Electro Scooter
        electro_scooter = ElectroScooter(
            name=name, battery_level=battery_level)
        # Add the Electro Scooter to the database
        db.session.add(electro_scooter)
        db.session.commit()
        return jsonify({"message": "Electro Scooter created successfully"}), 201
    except KeyError:
        return jsonify({"error": "Invalid request data"}), 400


@app.route('/api/electro-scooters/<int:scooter_id>', methods=['GET'])
def get_electro_scooter_by_id(scooter_id):
    # Find the Electro Scooter by ID
    scooter = ElectroScooter.query.get(scooter_id)
    if scooter is not None:
        return jsonify({
            "id": scooter.id,
            "name": scooter.name,
            "battery_level": scooter.battery_level
        }), 200
    else:
        return jsonify({"error": "Electro Scooter not found"}), 404
