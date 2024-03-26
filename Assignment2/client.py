# import grpc
import time
import random

# Import gRPC generated code (replace with actual generated code)
# from your_proto_file_pb2_grpc import RaftNodeStub
# from your_proto_file_pb2 import ServeClientArgs, ServeClientReply

class RaftClient:
    def __init__(self, node_addresses):
        self.node_addresses = node_addresses
        self.leader_address = self.discover_leader()
        
    def discover_leader(self):
        for address in self.node_addresses:
            # try:
                # # Establish connection with the node
                # with grpc.insecure_channel(address) as channel:
                #     # Create gRPC stub
                #     stub = RaftNodeStub(channel)
                #     # Send a test request to verify leader status
                #     response = stub.ServeClient(ServeClientArgs(Request=""))
                #     # If successful, set the leader address
                #     self.leader_address = address
            print(f"Leader discovered: {self.leader_address}")
            return True
            # except grpc.RpcError:
            #     # Error handling - leader not available
            #     print(f"Node at {address} not available, trying next...")
            #     continue
        # print("No leader available")
        # return False

def serve_client(self, request):
    # Retry until leader discovered or no leader available
    while not self.leader_address:
        if not self.discover_leader():
            # Retry after a delay
            time.sleep(1)
            continue

    # Retry until successful request or leader changes
    while True:
        try:
            # Establish connection with the leader node
            # with grpc.insecure_channel(self.leader_address) as channel:
            #     # Create gRPC stub
            #     stub = RaftNodeStub(channel)
            #     # Send request to the leader
            #     response = stub.ServeClient(request)
            #     # Return the response
            #     return response
            print("Simulated gRPC call: ServeClient")
            # Simulate different responses for SET and GET requests
            if request.Request.startswith("SET"):
                # Simulate busy response or no response for SET requests
                print("Simulating busy or no response for SET request")
                return None
            elif request.Request.startswith("GET"):
                # Allow previous leader to respond to GET requests during election
                print("Simulating response for GET request")
                return "Simulated data for GET request"  # Replace with actual data
        except grpc.RpcError as e:
            # Error handling - leader not available
            print(f"Error: {e}")
            print("Leader not available, retrying...")
            # Reset leader address and try to discover new leader
            self.leader_address = None
            # Attempt to discover a new leader
            self.discover_leader()

        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            print("Retrying...")
            time.sleep(1)


if __name__ == "__main__":
    # Initialize RaftClient with a list of leader IP addresses and ports
    node_addresses = ["leader1_ip:port", "leader2_ip:port", "leader3_ip:port"] 
    client = RaftClient(node_addresses)
    
    client.discover_leader()
    
    while True:
        #take client requests
        request = input("Enter your request: ")
        # Serve the client request
        if request == "exit":
            break
        else:
            response = client.serve_client(request)
        