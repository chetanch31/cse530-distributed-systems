import random
import sys
import time
from threading import Thread
import os

import grpc
from concurrent import futures

from grpc._channel import _InactiveRpcError

import raft_pb2
import raft_pb2_grpc
import schedule

# Define gRPC communication here (not implemented in this code snippet)

class Node(raft_pb2_grpc.RaftNodeServicer):
    node_count = 0  # Class attribute to keep track of node count

    def __init__(self, node_id, peer_nodes):
        Node.node_count = len(peer_nodes) + 1
        self.node_id = node_id
        self.peer_nodes = peer_nodes
        self.state = "follower"
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.heartbeat_timeout = 1  # Heartbeat timeout (in seconds)
        self.lease_duration = 7  # Lease duration (in seconds)
        self.leader_id = 0
        self.election_timer = self.generate_random_float()
        self.heartbeat_timer = None
        self.hearbeat_detection = False
        self.x = 0
        # self.serve()
        # self.channel = grpc.insecure_channel("34.133.227.248:50051")
        # self.stub = task_pb2_grpc.MarketStub(self.channel)

        print(f"Node {self.node_id} created.")

    # def serve(self):
    #     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    #     raft_pb2_grpc.add_RaftNodeServicer_to_server(self, server=server)
    #     print(f"Started listening at {self.peer_nodes[self.node_id]}")
    #     server.add_insecure_port(self.peer_nodes[self.node_id])
    #     server.start()
    #

    def ServeClient(self, request, context):

        response = raft_pb2.ServeClientReply()
        print(request)

        if request.request == "ping" and self.leader_id == self.node_id:
            response.data = "data"
            response.leaderId = str(self.leader_id)
            response.success = True

        else:
            response.data = "data"
            response.leaderId = str(self.leader_id)
            response.success = False

        return response
    def AppendEntries(self, request, context):

        if request.isHeartbeat:
            # The current request is just an heartbeat
            self.x = 0
            return raft_pb2.AppendEntriesResponse(term=self.current_term, success=True)

        if request.term < self.current_term:
            return raft_pb2.AppendEntriesResponse(term=self.current_term, success=False)

        if len(self.log) < request.prevLogIndex or (
                len(self.log) > 0 and self.log[request.prevLogIndex - 1].term != request.prevLogTerm):
            return raft_pb2.AppendEntriesResponse(term=self.current_term, success=False)

        # Step 3: If an existing entry conflicts with a new one, delete the existing entry and all that follow it
        # This step can be omitted if you handle log consistency elsewhere

        for entry in request.entries:
            if len(self.log) < entry.index:
                self.log.append(entry)
            else:
                self.log[entry.index - 1] = entry

        if request.leaderCommit > self.commit_index:
            self.commit_index = min(request.leaderCommit, len(self.log))

        self.current_term = request.term
        return raft_pb2.AppendEntriesResponse(term=self.current_term, success=True)

    def RequestVote(self, request, context):
        response = raft_pb2.RequestVoteResponse()
        response.term = self.current_term

        # Check if the candidate's term is less than the current term
        if request.term < self.current_term:
            response.voteGranted = False
            return response

        # Check if the node has already voted for a candidate in this term
        if self.voted_for is None or self.voted_for == request.candidateId:
            # Check if the candidate’s log is at least as up-to-date as the receiver’s log
            if (request.lastLogTerm > self.log[-1].term) or \
                    (request.lastLogTerm == self.log[-1].term and request.lastLogIndex >= len(self.log) - 1):
                response.voteGranted = True
                self.voted_for = request.candidateId
                return response

        # If the conditions are not met, do not grant the vote
        response.voteGranted = False
        return response

    def start(self):
        time.sleep(10)
        # Start the node's main loop in a separate thread
        # Thread(target=self.run).start()
        self.run()

    def run(self):
        print(f"Node {self.node_id} is running and active.")

        """Thread(target=self.hearbeat_sensor).start()
        self.create_node_files(self.node_id)

        if (self.hearbeat_detection):
            self.leader_id = 1  # its the index no in IP list
            print("Leader is present")
            self.state = "follower"
        self.create_node_files(self.node_id)

        # while True:
        # Check if there is a leader present

        if self.leader_id is None:
            # No leader present, start an election
            self.state = "candidate"""
        
        self.state = "leader"

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

            while True:
                # listen for messages from grpc
                self.receive_message()

        # ensure that it is actively counting the time not that the absolute values are greater

    def candidate_behavior(self):
        # Candidate behavior
        print("No Leader detected, Becoming a Candidate ")
        self.state = "candidate"

        # Prepare the RequestVoteRequest message
        request = raft_pb2.RequestVoteRequest()
        request.term = self.current_term
        request.candidateId = self.node_id
        request.lastLogIndex = len(self.log) - 1 if self.log else 0
        request.lastLogTerm = self.log[-1].term if self.log else 0

        # Send the request to each peer node and gather responses
        votes_received = 1  # Counting self vote
        for node_id, peer_node in enumerate(self.peer_nodes, start=0):
            if node_id == self.node_id:
                continue

            response = self.request_vote(peer_node, request)
            if response.voteGranted:
                votes_received += 1

        # Check if the candidate received the majority of votes
        if votes_received > len(self.peer_nodes) // 2:
            # Become the leader if the candidate received the majority of votes
            print("Received majority of votes. Becoming the leader.")
            self.state = "leader"
            self.leader_id = self.node_id
            # Perform leader initialization tasks here
            self.leader_behavior()
        else:
            # Did not receive the majority of votes, remain a candidate
            print("Did not receive majority of votes. Remaining a candidate.")
            self.x = 0
            self.follower_behavior()

        # response=self.request_votes()

        # response should be the list of votes received from all peer nodes
        # if response>=len(peer_nodes)/2:
        #     self.state="leader"
        #     self.leader_id=self.node_id
        # grpc sends message to all peer nodes that new leader is eleceted
        # leader_message={"type":"Leader","term":self.current_term}

        # self.leader_behavior()

        # get votes back

    def request_vote(self, peer_node, request):
        print(peer_node)
        try:
            channel = grpc.insecure_channel(peer_node)
            stub = raft_pb2_grpc.RaftNodeStub(channel)
            response = stub.RequestVote(request=request)
            return response
        except _InactiveRpcError:
            print(f"The node at {peer_node} is offline")

    def receive_message(self, message):
        if message["type"] == "AppendEntries":
            self.handle_append_entries(message)
        elif message["type"] == "RequestVote":
            self.receive_vote_request(message)
            if self.state == "leader":
                # send the node that requested vote through grpc the lease time of the leader
                pass
        elif message["type"] == "Heartbeat":
            self.handle_heartbeat(message)
            self.x = 0
        else:
            print("Unknown message type")

    def leader_behavior(self):
        print(f"Node {self.node_id} is the leader")
        self.leader_id = self.node_id
        self.current_term +=1
        Thread(target=self.send_heartbeats()).start()


    def request_votes(self):
        # Send vote requests to peer nodes
        for peer_node in self.peer_nodes:
            # Send a vote request to the peer node using grpc
            # response = self.____(peer_node)
            self.response = {"term": 1, "voteGranted": True}
            return self.response

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
        print("Sending heartbeats")
        while True:
            print("Sending heartbeats inside true")
            if self.state!="leader":
                break

            # Send heartbeats to followers
            request = raft_pb2.AppendEntriesRequest()
            request.term = self.current_term
            request.leaderId = self.node_id
            request.prevLogIndex = len(self.log) - 1 if self.log else 0  # Index of the last log entry
            request.prevLogTerm = self.log[-1].term if self.log else 0  # Term of the last log entry
            request.leaderCommit = self.commit_index  # Index of highest log entry known to be committed
            request.leaderLeaseDuration = self.lease_duration
            request.isHeartbeat = True

            for node_id, peer_node in enumerate(self.peer_nodes, start=0):
                if node_id == self.node_id:
                    continue

                print(peer_node)
                try:
                    channel = grpc.insecure_channel(peer_node)
                    stub = raft_pb2_grpc.RaftNodeStub(channel)
                    response = stub.AppendEntries(request=request)
                    print(f"Got response: {response}")
                except _InactiveRpcError:
                    print(f"The node at {peer_node} is offline")

                time.sleep(1)

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
            if (self.x == 1):
                self.hearbeat_detection = False
                self.candidate_behavior()

            if self.leader_id is not None:
                self.hearbeat_detection = True

            self.x = self.x + 1
            time.sleep(self.election_timer)  # Sleep for seconds before checking again


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python filename.py <node_id>")
        sys.exit(1)

    node_id = int(sys.argv[1])
    peer_nodes = ["localhost:50589", "localhost:50590"]

    node = Node(node_id=node_id, peer_nodes=peer_nodes)
    node_ip = peer_nodes[node_id]

    server = grpc.server(futures.ThreadPoolExecutor())
    raft_pb2_grpc.add_RaftNodeServicer_to_server(node, server)

    server.add_insecure_port(node_ip)
    server.start()

    print(f"Server started for node {node_id}. Listening on {node_ip}")

    time.sleep(1)
    Thread(target=node.start()).start()

    server.wait_for_termination()
    
    """while True:        
        time.sleep(1)
        node.start()
        print(f"Node {node_id} is running...")"""