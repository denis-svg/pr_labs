# Import necessary modules
from flask import request, jsonify, current_app
from models.database import db
from models.electro_scooter import ElectroScooter
from __main__ import app
from flasgger import swag_from
import requests


@swag_from({
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "battery_level": {
                            "type": "number"
                        },
                        "token": {
                            "type": "string"
                        }
                    },
                "required": True,
                "description": "JSON body containing registration data"
            }
        },
    ],
    "responses": {
        201: {
            "description": "Registration successful",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "Electro Scooter created successfully"
                    },
                }, }
        },
        406: {"description": "Bad request Method"},
        400: {"description": "Invalid Json",
              "schema": {
                  "type": "object",
                  "properties": {
                          "error": {
                              "type": "Invalid request data"
                          },
                  }, }},
    },
})
@app.route('/api/electro-scooters', methods=['POST'])
def create_electro_scooter():
    try:
        # Get data from the request body
        data = request.get_json()
        print(data)
        # Validate and extract required parameters
        name = data['name']
        battery_level = data['battery_level']
        token = None
        if current_app.config['LOADED_OBJECT'].raft_state == "FOLLOWER":
            token = data["token"]
            if token != current_app.config['LOADED_OBJECT'].leader_credentials["token"]:
                return jsonify({"error": "Forbiden access"}), 403
        if current_app.config['LOADED_OBJECT'].raft_state == "LEADER":
            # Forward the request to another server
            for follower in current_app.config['LOADED_OBJECT'].follower_credentials:
                host = follower["host"]
                port = follower["port"]
                print(follower)
                forward_url = f"http://{host}:{port}/api/electro-scooters"
                forward_data = {
                    "name": name,
                    "battery_level": battery_level,
                    "token": current_app.config['LOADED_OBJECT'].service_info["token"]
                }
                try:
                    # Make the HTTP request
                    requests.post(forward_url, json=forward_data)
                except Exception as e:
                    return jsonify({"error": f"Forwarding {host}:{port} request failed"}), 500

        # Create a new Electro Scooter
        electro_scooter = ElectroScooter(
            name=name, battery_level=battery_level)
        # Add the Electro Scooter to the database
        db.session.add(electro_scooter)
        db.session.commit()
        return jsonify({"message": "Electro Scooter created successfully"}), 201
    except KeyError:
        return jsonify({"error": "Invalid request data"}), 400


@swag_from({
    "parameters": [
        {
            "name": "scooter_id",
            "in": "path",
            "type": "number",
            "required": "true"
        }
    ],
    "responses": {
        201: {
            "description": "Registration successful",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "number"
                    },
                    "name": {
                        "type": "string"
                    },
                    "battery_level": {
                        "type": "string"
                    },
                }, }
        },
        406: {"description": "Bad request Method"},
        404: {"description": "Invalid Json",
              "schema": {
                  "type": "object",
                  "properties": {
                          "error": {
                              "type": "Electro Scooter not found"
                          },
                  }, }},
    },
})
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


@swag_from({
    "parameters": [
        {
            "name": "scooter_id",
            "in": "path",
            "type": "number",
            "required": "true"
        },
        {
            "name": "body",
            "in": "body",
            "schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "battery_level": {
                            "type": "number"
                        },
                        "token": {
                            "type": "string"
                        }
                    },
                "required": True,
                "description": "JSON body containing registration data"
            }
        },
    ],
    "responses": {
        200: {
            "description": "Registration successful",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "Electro Scooter updated successfully"
                    },
                }, }
        },
        406: {"description": "Bad request Method"},
        404: {"description": "Invalid Json",
              "schema": {
                  "type": "object",
                  "properties": {
                          "error": {
                              "type": "Electro Scooter not found"
                          },
                  }, }},
    },
})
@app.route('/api/electro-scooters/<int:scooter_id>', methods=['PUT'])
def update_electro_scooter(scooter_id):
    try:
        # Find the Electro Scooter by ID
        scooter = ElectroScooter.query.get(scooter_id)
        if scooter is not None:
            # Get data from the request body
            data = request.get_json()
            print(data)
            token = None
            if current_app.config['LOADED_OBJECT'].raft_state == "FOLLOWER":
                token = data['token']
                if token != current_app.config['LOADED_OBJECT'].leader_credentials["token"]:
                    return jsonify({"error": "Forbiden access"}), 403
            if current_app.config['LOADED_OBJECT'].raft_state == "LEADER":
                # Forward the request to another server
                for follower in current_app.config['LOADED_OBJECT'].follower_credentials:
                    host = follower["host"]
                    port = follower["port"]
                    # change this forward to be adelete
                    forward_url = f"http://{host}:{port}/api/electro-scooters/{scooter_id}"
                    headers = {
                        "accept": "application/json",
                        "Content-Type": "application/json",
                    }
                    data = {
                        "battery_level": data["battery_level"],
                        "name": data["name"],
                        "token": current_app.config['LOADED_OBJECT'].service_info["token"]
                    }
                    try:
                        # Make the HTTP request
                        requests.put(
                            forward_url, headers=headers, json=data)
                    except Exception as e:
                        return jsonify({"error": f"Forwarding {host}:{port} request failed"}), 500

            # Update the Electro Scooter properties
            scooter.name = data.get('name', scooter.name)
            scooter.battery_level = data.get(
                'battery_level', scooter.battery_level)
            db.session.commit()
            return jsonify({"message": "Electro Scooter updated successfully"}), 200
        else:
            return jsonify({"error": "Electro Scooter not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@swag_from({
    "parameters": [
        {
            "name": "scooter_id",
            "in": "path",
            "type": "number",
            "required": "true"
        },
        {"in": 'header',
            'name': 'X-Delete-Password',  # <---- HTTP header name
         "required": "true",
         "type": "string", },
        {"in": 'header',
            'name': 'token',  # <---- HTTP header name
         "required": "true",
         "type": "string", },
    ],
    "responses": {
        200: {
            "description": "Registration successful",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "Electro Scooter updated successfully"
                    },
                }, }
        },
        406: {"description": "Bad request Method"},
        404: {"description": "Invalid Json",
              "schema": {
                  "type": "object",
                  "properties": {
                          "error": {
                              "type": "Electro Scooter not found"
                          },
                  }, }},
    },
})
@app.route('/api/electro-scooters/<int:scooter_id>', methods=['DELETE'])
def delete_electro_scooter(scooter_id):
    try:
        # Find the Electro Scooter by ID
        scooter = ElectroScooter.query.get(scooter_id)
        if scooter is not None:
            # Get the password from the request headers
            password = request.headers.get('X-Delete-Password')
            token = None
            if current_app.config['LOADED_OBJECT'].raft_state == "FOLLOWER":
                token = request.headers.get('token')
                if token != current_app.config['LOADED_OBJECT'].leader_credentials["token"]:
                    return jsonify({"error": "Forbiden access"}), 403
            if current_app.config['LOADED_OBJECT'].raft_state == "LEADER":
                # Forward the request to another server
                for follower in current_app.config['LOADED_OBJECT'].follower_credentials:
                    host = follower["host"]
                    port = follower["port"]
                    # change this forward to be adelete
                    forward_url = f"http://{host}:{port}/api/electro-scooters/{scooter_id}"
                    headers = {
                        "accept": "application/json",
                        "X-Delete-Password": password,
                        "token": current_app.config['LOADED_OBJECT'].service_info["token"]
                    }
                    try:
                        # Make the HTTP request
                        requests.delete(
                            forward_url, headers=headers)
                    except Exception as e:
                        return jsonify({"error": f"Forwarding {host}:{port} request failed"}), 500
                    
            # Check if the provided password is correct
            if password == 'faf':  # Replace with your actual password
                db.session.delete(scooter)
                db.session.commit()
                return jsonify({"message": "Electro Scooter deleted successfully"}), 200
            else:
                return jsonify({"error": "Incorrect password"}), 401
        else:
            return jsonify({"error": "Electro Scooter not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
