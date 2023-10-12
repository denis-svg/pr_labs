#client.py

import socket
import threading
import json
import os
import base64

# Server configuration
HOST = '127.0.0.1'  # Server's IP address
PORT = 8080       # Server's port

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Connect to the server
client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")

# Function to receive and display messages
def receive_messages():
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break  # Exit the loop when the server disconnects
        message = message.replace("'", '"')
        message = json.loads(message)
        if message['type'] == "message":
            print(f"\n{message['payload']['room']}/{message['payload']['name']}:{message['payload']['text']}")

        elif message['type'] == "size":
            # Received an image/file from the client
            filesize = message["fsize"]

            message = client_socket.recv(int(filesize) * 2).decode('utf-8')
            
            message = message.replace("'", '"')
            
            message = json.loads(message)
            
            filename = message["payload"]["filename"]
            filedata = message["payload"]["filedata"]

            with open(message['payload']['name'] + filename, "wb") as file:
                file.write(base64.b64decode(filedata))
                
            print(f"\n{message['payload']['room']}/{message['payload']['name']} sent a file: {filename}")

def get_general_info():
    name = input("Enter your name:")
    room = input("Enter a room:")
    
    return {
            "name":name,
            "room":room
            }

def init(gen_info):
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True  # Thread will exit when the main program exits
    receive_thread.start()
    json_sent = {
        "type": "connect_ack",
        "payload": {
            "room":gen_info["room"],
            "name":gen_info["name"]
        }
    }

    client_socket.send(str(json_sent).encode('utf-8'))

def has_extension(filename, extension):
    return filename.endswith(extension) and " " not in filename

gen_info = get_general_info()
init(gen_info)

while True:
    message = input(f"{gen_info['room']}/{gen_info['name']}:")

    if message.lower() == 'exit':
        break

    if has_extension(message, ".txt") or has_extension(message, ".png") or has_extension(message, ".py"):
        file = open(message, "rb")
        file_size = os.path.getsize(message)
        data = file.read()
        file.close()
        print("Client", data, base64.b64encode(data).decode('ascii'))

        client_socket.send(str({"type":"size",
                                "fsize":file_size}).encode('utf-8'))

        json_sent = {
            "type": "image",
            "payload":{
                "filename":message,
                "filesize":file_size,
                "filedata":base64.b64encode(data).decode('ascii'),
                "room":gen_info["room"],
                "name":gen_info["name"],
            }
        }
    else:
        json_sent = {
            "type": "message",
            "payload":{
                "text":message,
                "room":gen_info["room"],
                "name":gen_info["name"],
            }
        }

    client_socket.send(str(json_sent).encode('utf-8'))
 
# Close the client socket when done
client_socket.close()