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

        elif message['type'] == "image":
            # Received an image/file from the client
            filesize = message["filesize"]
            filedata = b""
            total_received = 0

            while total_received < filesize:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                filedata += chunk
                total_received += len(chunk)
            
            message = client_socket.recv(1024).decode('utf-8')
            message = message.replace("'", '"')
            message = json.loads(message)
            
            filename = message["payload"]["filename"]

            with open("client_" + filename, "wb") as file:
                file.write(filedata)
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
        print("Client", data)
        client_socket.send(str({"type":"image",
                                "filesize":file_size}).encode('utf-8'))


        # Then, send the image data in chunks
        chunk_size = 1024
        total_sent = 0
        while total_sent < file_size:
            chunk = data[total_sent:total_sent + chunk_size]
            client_socket.send(chunk)
            total_sent += len(chunk)

        json_sent = {
            "type": "image",
            "payload": {
                "filename": message,
                "room": gen_info["room"],
                "name": gen_info["name"],
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