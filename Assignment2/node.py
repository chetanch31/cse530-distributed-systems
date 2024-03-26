import random
import time
from threading import Thread
import os

# Define gRPC communication here (not implemented in this code snippet)

class RaftNode:
    node_count = 0  # Class attribute to keep track of node count

    def __init__(self, node_id, peer_nodes):
        RaftNode.node_count = len(peer_nodes)+1
        self.node_id = node_id
        self.peer_nodes = peer_nodes
        self.state = "follower"
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.election_timeout = random.randint(5, 10)  # Randomized election timeout
        self.heartbeat_timeout = 1  # Heartbeat timeout (in seconds)
        self.lease_duration = 7  # Lease duration (in seconds)
        self.leader_id = None
        self.election_timer = self.generate_random_float()
        self.heartbeat_timer = None
        self.hearbeat_detection = False
        self.x=0

        print(f"Node {self.node_id} created.")

    def start(self):
        # Start the node's main loop in a separate thread
        Thread(target=self.run).start()

    def run(self):
        print(f"Node {self.node_id} is running and active.")
        
        Thread(target=self.hearbeat_sensor).start()
        self.create_node_files(self.node_id)
        
        if(self.hearbeat_detection):
            self.leader_id = 1 #its the index no in IP list
            print("Leader is present")
            self.state="follower"
        self.create_node_files(self.node_id)

        #while True:
            # Check if there is a leader present
        
        if self.leader_id is None:
            # No leader present, start an election
            self.state = "candidate"

        if self.state == "follower":
            self.follower_behavior()
        elif self.state == "candidate":
            self.candidate_behavior()
        elif self.state == "leader":
            self.leader_behavior()

    def follower_behavior(self):
        
        # Follower behavior
        print(f"Node {self.node_id} is in Follower state.")
        if self.election_timer is None:
            self.start_election_timer()
            
            #listen for messages from grpc
            
            while True:
                #listen for messages from grpc
                
                self.receive_message()
            
        #ensure that it is actively counting the time not that the absolute values are greater
        elif self.election_timer >= self.election_timeout:
            self.state = "candidate"
            self.reset_election_timer()

    def candidate_behavior(self):
        # Candidate behavior
        print("No Leader detected, Becomming a Candidate ")
        self.state = "candidate"
        response=self.request_votes()

        #get votes back
        
        
    def receive_message(self, message):
        if message["type"] == "AppendEntries":
            self.handle_append_entries(message)
        elif message["type"] == "RequestVote":
            self.receive_vote_request(message)
        elif message["type"] == "Heartbeat":
            self.handle_heartbeat(message)
        else:
            print("Unknown message type")

    def leader_behavior(self):
        # Leader behavior
        if self.heartbeat_timer is None:
            self.start_heartbeat_timer()
            self.acquire_lease()
            self.send_heartbeats()
            #what is happening here
        elif self.heartbeat_timer >= self.heartbeat_timeout:
            self.reset_heartbeat_timer()

    def request_votes(self):
        # Send vote requests to peer nodes
        for peer_node in self.peer_nodes:
            #if peer_node.request_vote(self.current_term, self.node_id):
                # Received vote from peer node
                pass

    def receive_vote_request(self, response):
                
        term, voteGrangted = response["term"], response["voteGranted"]
        # Follower's response to a vote request from a candidate
        if term < self.current_term:
            return False
        elif term >= self.current_term & self.voted_for is None:
            self.current_term = term
            return True
        else:
            return False

    def start_election_timer(self):
        # Start the election timer
        self.election_timer = 0

    # def reset_election_timer(self):
    #     # Reset the election timer
    #     self.election_timer = None

    def start_heartbeat_timer(self):
        # Start the heartbeat timer
        self.heartbeat_timer = 0

    def reset_heartbeat_timer(self):
        # Reset the heartbeat timer
        self.heartbeat_timer = None

    def acquire_lease(self):
        # Acquire the leader lease
        pass

    def send_heartbeats(self):
        # Send heartbeats to followers
        pass

    def append_entries(self, term, leader_id):
        # Append entries to the log
        pass

    def receive_append_entries(self, term, leader_id):
        # Follower's response to append entries from the leader
        pass

    def create_node_files(self, node_id):
        base_dir = 'assignment'
        node_dir = f'logs_node_{node_id}'
        logs_file = 'logs.txt'
        metadata_file = 'metadata.txt'
        dump_file = 'dump.txt'

        # Create the base directory if it doesn't exist
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Create the node directory under the base directory
        node_path = os.path.join(base_dir, node_dir)
        if not os.path.exists(node_path):
            os.makedirs(node_path)

        # Create logs.txt, metadata.txt, and dump.txt files under the node directory
        logs_path = os.path.join(node_path, logs_file)
        metadata_path = os.path.join(node_path, metadata_file)
        dump_path = os.path.join(node_path, dump_file)

        # Create empty files if they don't exist
        open(logs_path, 'a').close()
        open(metadata_path, 'a').close()
        open(dump_path, 'a').close()

        print(f"Files created for node {node_id} at {node_path}")

    def generate_random_float(self):
        # Generate a random float between 5 to 10
        timer = random.uniform(5, 10)
        print(f"set election timer to {timer} seconds")
        return timer

    def hearbeat_sensor(self):
        print("Heartbeat sensor started")
        # Check for heartbeat detection in a loop
        while True:
            print("Node Timeout started")
            
            print(self.x)
            if(self.x==1):
                self.hearbeat_detection=False
                self.candidate_behavior()

            self.hearbeat_detection = True
            self.x = self.x+1
            time.sleep(self.election_timer)  # Sleep for seconds before checking again
            
if __name__ == "__main__":
    # Define peer nodes (replace with actual node instances)
    peer_nodes = ['IP1','IP2']

    # Create and start Raft nodes
    node1 = RaftNode(node_id=1, peer_nodes=peer_nodes)
    # node2 = RaftNode(node_id=2, peer_nodes=peer_nodes)
    # node3 = RaftNode(node_id=3, peer_nodes=peer_nodes)

    node1.start()
    print("Node 1 is running...")
    # node2.start()
    # node3.start()
