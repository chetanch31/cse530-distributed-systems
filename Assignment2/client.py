# import grpc
import time
import random

import grpc
from grpc._channel import _InactiveRpcError

import raft_pb2
import raft_pb2_grpc


class RaftClient:
    def __init__(self, node_addresses):
        self.node_addresses = node_addresses
        self.leader_address = None

    def discover_leader(self):
        for address in self.node_addresses:
            try:
                with grpc.insecure_channel(address) as channel:
                    stub = raft_pb2_grpc.RaftNodeStub(channel)
                    response = stub.ServeClient(raft_pb2.ServeClientArgs(request="ping"))
                    if response.success:
                        self.leader_address = address
                        print(f"Leader discovered: {self.leader_address}")
                        return True

            except _InactiveRpcError:
                print(f"Node at {address} not available, trying next")
                continue

        return False

    def serve_client(self, request):
        while not self.leader_address:
            if not self.discover_leader():
                time.sleep(1)
                continue

        while True:
            try:
                with grpc.insecure_channel(self.leader_address) as channel:
                    stub = raft_pb2_grpc.RaftNodeStub(channel)
                    response = stub.ServeClient(raft_pb2.ServeClientArgs(request=request))
                    print(response)
                    return response

            except grpc.RpcError as e:
                print(f"Error: {e}")
                print("Leader not available, retrying...")
                self.leader_address = None
                self.discover_leader()

            except Exception as e:
                print(f"Error: {e}")
                print("Retrying...")
                time.sleep(1)


if __name__ == "__main__":
    node_addresses = ["localhost:50589", "localhost:50590"]
    client = RaftClient(node_addresses)

    while client.leader_address is None:
        client.discover_leader()

    while True:
        # take client requests
        request = input("Enter your request: ")
        # Serve the client request
        if request == "exit":
            break
        else:
            response = client.serve_client(request)
