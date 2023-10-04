import signal
import sys
import socket
import json
import re

HOST = '127.0.0.1'
PORT = 8080
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Server is listening on {HOST}:{PORT}")


products = [
  {
    "name" : "Fluent Python: Clear, Concise, and Effective Programming",
    "author" : "Luciano Ramalho",
    "price" : 39.95,
    "description" : "Don't waste time bending Python to fit patterns you've learned in other languages. Python's simplicity lets you become productive quickly, but often this means you aren't using everything the language has to offer. With the updated edition of this hands-on guide, you'll learn how to write effective, modern Python 3 code by leveraging its best ideas. "
  },
  {
    "name" : "Introducing Python: Modern Computing in Simple Packages",
    "author" : "Bill Lubanovic",
    "price" : 27.49,
    "description" : "Easy to understand and fun to read, this updated edition of Introducing Python is ideal for beginning programmers as well as those new to the language. Author Bill Lubanovic takes you from the basics to more involved and varied topics, mixing tutorials with cookbook-style code recipes to explain concepts in Python 3. End-of-chapter exercises help you practice what you’ve learned."
  }
]

def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def home():
    return "<h1>Home Page</h1>"

def about():
    return "<h1> About Page </h1>"

def getProduct(i):
    if i > len(products) - 1:
        return None
    product = products[i]
    return f'<div><h1>{product["name"]}</h1><h1>{product["author"]}</h1><h1>{product["price"]}</h1><h1>{product["description"]}</h1></div>'

def getProducts():
    html = ""
    for i in range(len(products)):
        product_html = getProduct(i)
        html += f"<h1>{i}</h1>" + product_html + "<br>"

    return html

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    request_data = client_socket.recv(1024).decode('utf-8')
    # print(f"Received Request:\n{request_data}")
    request_lines = request_data.split('\n')
    status = 200
    request_line = request_lines[0].strip().split()
    if request_line:
        response_content = "Could not find the page"
        method = request_line[0]
        path = request_line[1]
        if method == "GET":
            if path == '/home':
                response_content = home()
                status = 200
            elif path == "/about":
                response_content = about()
                status = 200
            elif path[0:len('/product/')] == '/product/':
                try:
                    p_number = int(path[len('/product/'):len(path) + 1])
                    response_content = getProduct(p_number)
                    if response_content is None:
                        status = 404
                        response_content = "Content doesnt exists"
                    status = 200
                except ValueError:
                    status = 404
                finally:
                    if path == '/product/':
                        response_content = getProducts()
                        status = 200
            else:
                status = 404

        response = f'HTTP/1.1 {status} OK\nContent-Type: text/html\n\n{response_content}'
        client_socket.send(response.encode('utf-8'))
    client_socket.close()
