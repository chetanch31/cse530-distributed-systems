import grpc
import time
import random

# Import gRPC generated code (replace with actual generated code)
# from your_proto_file_pb2_grpc import RaftNodeStub
# from your_proto_file_pb2 import ServeClientArgs, ServeClientReply

class RaftClient:
    def __init__(self, leader_addresses):
        self.leader_addresses = leader_addresses
        self.leader_address = None

    def discover_leader(self):
        for address in self.leader_addresses:
            try:
                # Establish connection with the node
                with grpc.insecure_channel(address) as channel:
                    # Create gRPC stub
                    stub = RaftNodeStub(channel)
                    # Send a test request to verify leader status
                    response = stub.ServeClient(ServeClientArgs(Request=""))
                    # If successful, set the leader address
                    self.leader_address = address
                    print(f"Leader discovered: {self.leader_address}")
                    return True
            except grpc.RpcError:
                # Error handling - leader not available
                print(f"Node at {address} not available, trying next...")
                continue
        print("No leader available")
        return False

    def serve_client(self, request):
        # Retry until leader discovered or no leader available
        while not self.leader_address:
            if not self.discover_leader():
                time.sleep(1)
                continue

        # Retry until successful request or leader changes
        while True:
            try:
                # Establish connection with the leader node
                with grpc.insecure_channel(self.leader_address) as channel:
                    # Create gRPC stub
                    stub = RaftNodeStub(channel)
                    # Send request to the leader
                    response = stub.ServeClient(request)
                    # Return the response
                    return response
            except grpc.RpcError as e:
                # Error handling - leader not available
                print(f"Error: {e}")
                print("Leader not available, retrying...")
                # Reset leader address and try to discover new leader
                self.leader_address = None
                break
            except Exception as e:
                # Handle other exceptions
                print(f"Error: {e}")
                print("Retrying...")
                time.sleep(1)

if __name__ == "__main__":
    # Initialize RaftClient with a list of leader IP addresses and ports
    leader_addresses = ["leader1_ip:port", "leader2_ip:port", "leader3_ip:port"]  # Replace with actual leader addresses
    client = RaftClient(leader_addresses)

    # Example SET request
    set_request = ServeClientArgs(Request="SET key value")
    set_response = client.serve_client(set_request)
    print(f"SET Response: {set_response}")

    # Example GET request
    get_request = ServeClientArgs(Request="GET key")
    get_response = client.serve_client(get_request)
    print(f"GET Response: {get_response}")


class Raft:
    def __init__(self, ip, port, partitions):
        self.ip = ip
        self.port = port
        self.ht = HashTable()
        self.commit_log = CommitLog(file=f"commit-log-{self.ip}-{self.port}.txt")
        self.partitions = eval(partitions)
        self.conns = [[None]*len(self.partitions[i]) for i in range(len(self.partitions))]
        self.cluster_index = -1
        self.server_index = -1

        # Initialize commit log file
        commit_logfile = Path(self.commit_log.file)
        commit_logfile.touch(exist_ok=True)

        for i in range(len(self.partitions)):
            cluster = self.partitions[i]
            
            for j in range(len(cluster)):
                ip, port = cluster[j].split(':')
                port = int(port)
                
                if (ip, port) == (self.ip, self.port):
                    self.cluster_index = i
                    self.server_index = j
                    
                else: 
                    self.conns[i][j] = (ip, port)
        
        self.current_term = 1
        self.voted_for = -1
        self.votes = set()
        
        u = len(self.partitions[self.cluster_index])
        
        self.state = 'FOLLOWER' if len(self.partitions[self.cluster_index]) > 1 else 'LEADER'
        self.leader_id = -1
        self.commit_index = 0
        self.next_indices = [0]*u
        self.match_indices = [-1]*u
        self.election_period_ms = randint(1000, 5000)
        self.rpc_period_ms = 3000
        self.election_timeout = -1
        
        print("Ready....")