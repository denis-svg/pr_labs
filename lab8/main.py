import socket
import threading
import json
import sys
import pickle

# Raft states
FOLLOWER = "FOLLOWER"
LEADER = "LEADER"


class RaftNode:
    def __init__(self, service_info, node_id, udp_host="127.0.0.1", udp_port=5005):
        self.node_id = node_id
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.buffer_size = 1024
        self.raft_state = FOLLOWER
        self.leader_credentials = None
        self.follower_credentials = None
        self.service_info = service_info
        self.udp_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send_message(self, message, address):
        self.udp_socket.sendto(json.dumps(message).encode(), address)

    def start(self):
        try:
            self.udp_socket.bind((self.udp_host, self.udp_port))
            print(f"Node {self.node_id} is wants to be a leader")
            self.raft_state = LEADER
            self.leader_credentials = self.service_info
            # Starting to gather the information about the followers as they connect using UDP.
            self.follower_credentials = []
            message_counter = 0
            while True:
                if message_counter == 3 * 2:
                    break
                # Reading the message and the address from connection.
                message, address = self.udp_socket.recvfrom(self.buffer_size)
                message = json.loads(message.decode())
                if "acccept" in message:
                    self.send_message(self.service_info, address)
                else:
                    print(f"Leader node {self.node_id} received credentials {message}")
                    self.follower_credentials.append(message)
                message_counter += 1
            print(self.follower_credentials)

        except OSError:
            print(f"Node {self.node_id} will became a follower")
            self.send_message(
                {"acccept": 1}, (self.udp_host, self.udp_port))
            print(f"Node {self.node_id} sent an accept")
            message, address = self.udp_socket.recvfrom(self.buffer_size)
            message = json.loads(message.decode())
            print(f"Node {self.node_id} received leader's credentials {message}")
            self.leader_credentials = message
            self.send_message(self.service_info,
                              (self.udp_host, self.udp_port))


if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python main.py <port> <node_id>")
        sys.exit(1)

    # Extract port and node_id from command-line arguments
    port = int(sys.argv[1])
    node_id = int(sys.argv[2])

    # Create a node with specified port and node ID
    node = RaftNode({
        "host": "127.0.0.1",
        "port": port,
        "token": "secret"
    }, node_id=node_id)

    # Start the node
    node.start()

    with open(f'saved_object{node.node_id}.pkl', 'wb') as file:
        node.udp_socket = None
        pickle.dump(node, file)