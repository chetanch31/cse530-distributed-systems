import random
import threading
import time
import sys

import grpc
from concurrent import futures
import raft_pb2
import raft_pb2_grpc


class Node(raft_pb2_grpc.RaftNodeServicer):
    def __init__(self, node_id, peer_list):
        self.node_id = node_id
        self.peer_list = peer_list
        self.ip_addr = peer_list[self.node_id]

    def AppendEntries(self, request, context):
        print(f"Node {self.node_id}: Received AppendEntries RPC")
        print(f"Node {self.node_id}: Request:", request)
        # Generate a random response
        response = raft_pb2.AppendEntriesResponse(term=random.randint(1, 100), success=random.choice([True, False]))
        return response

    def RequestVote(self, request, context):
        print(f"Node {self.node_id}: Received RequestVote RPC")
        print(f"Node {self.node_id}: Request:", request)
        # Generate a random response
        response = raft_pb2.RequestVoteResponse(term=random.randint(1, 100), voteGranted=random.choice([True, False]))
        return response

    def send_random_requests(self):
        print("Starting to send requests")
        while True:
            time.sleep(random.uniform(1, 5))  # Random sleep time
            peer_id = 1 if self.node_id == 0 else 0  # Select the other peer
            peer_addr = self.peer_list[peer_id]
            if random.random() < 0.5:  # Randomly choose RPC type
                request = raft_pb2.AppendEntriesRequest(term=random.randint(1, 100), leaderId=self.node_id)
                with grpc.insecure_channel(peer_addr) as channel:
                    stub = raft_pb2_grpc.RaftNodeStub(channel)
                    response = stub.AppendEntries(request)
                    print(f"Node {self.node_id}: Sent AppendEntries request to Node {peer_id}. Response:", response)
            else:
                request = raft_pb2.RequestVoteRequest(term=random.randint(1, 100), candidateId=self.node_id)
                with grpc.insecure_channel(peer_addr) as channel:
                    stub = raft_pb2_grpc.RaftNodeStub(channel)
                    response = stub.RequestVote(request)
                    print(f"Node {self.node_id}: Sent RequestVote request to Node {peer_id}. Response:", response)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python filename.py <node_id>")
        sys.exit(1)

    node_id = int(sys.argv[1])
    peer_list = ["127.0.0.1:50500", "127.0.0.1:50501"]

    node = Node(node_id, peer_list)
    ip_addr = peer_list[node_id]

    server = grpc.server(futures.ThreadPoolExecutor())
    raft_pb2_grpc.add_RaftNodeServicer_to_server(node, server)

    server.add_insecure_port(ip_addr)
    server.start()
    print(f"Listening on {ip_addr}")
    while True:
        time.sleep(1)
        node.send_random_requests()





