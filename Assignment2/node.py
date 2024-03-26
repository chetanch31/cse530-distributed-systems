import random
import time
from threading import Thread

# Define gRPC communication here (not implemented in this code snippet)

class RaftNode:
    def __init__(self, node_id, peer_nodes):
        self.RaftNode.node_count += 1
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
        self.lease_duration = 5  # Lease duration (in seconds)
        self.leader_id = None
        self.election_timer = None
        self.heartbeat_timer = None
        
        print(f"Node {self.node_id} created.")

    def start(self):
        # Start the node's main loop in a separate thread
        Thread(target=self.run).start()


    def run(self):
        
        print(f"Node {self.node_id} is running and active.")

        while True:
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
            time.sleep(0.1)

    def follower_behavior(self):
        # Follower behavior
        if self.election_timer is None:
            self.start_election_timer()
        elif self.election_timer >= self.election_timeout:
            self.state = "candidate"
            self.reset_election_timer()

    def candidate_behavior(self):
        # Candidate behavior
        if self.election_timer is None:
            self.start_election_timer()
            self.current_term += 1
            self.voted_for = self.node_id
            self.request_votes()
        elif self.election_timer >= self.election_timeout:
            self.reset_election_timer()

    def leader_behavior(self):
        # Leader behavior
        if self.heartbeat_timer is None:
            self.start_heartbeat_timer()
            self.acquire_lease()
            self.send_heartbeats()
        elif self.heartbeat_timer >= self.heartbeat_timeout:
            self.reset_heartbeat_timer()

    def request_votes(self):
        # Send vote requests to peer nodes
        for peer_node in self.peer_nodes:
            if peer_node.request_vote(self.current_term, self.node_id):
                # Received vote from peer node
                pass

    def receive_vote_request(self, term, candidate_id):
        # # Follower's response to a vote request from a candidate
        # # does it compare the candidate's term with its own term?
        # if term > self.current_term:
        #     self.current_term = term
        #     self.state = "follower"
        #     self.voted_for = None
        # if self.voted_for is None or self.voted_for == candidate_id:
        #     return True
        return False

    def start_election_timer(self):
        # Start the election timer
        self.election_timer = 0

    def reset_election_timer(self):
        # Reset the election timer
        self.election_timer = None

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


if __name__ == "__main__":
    # Define peer nodes (replace with actual node instances)
    peer_nodes = []

    # Create and start Raft nodes
    node1 = RaftNode(node_id=1, peer_nodes=peer_nodes)
    # node2 = RaftNode(node_id=2, peer_nodes=peer_nodes)
    # node3 = RaftNode(node_id=3, peer_nodes=peer_nodes)

    node1.start()
    print("Node 1 is running...")
    # node2.start()
    # node3.start()
    
    
