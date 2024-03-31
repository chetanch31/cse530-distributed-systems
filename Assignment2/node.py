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
        self.voted_for = -1
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.heartbeat_timeout = 1  # Heartbeat timeout (in seconds)
        self.lease_duration = 7  # Lease duration (in seconds)
        self.leader_id = None
        self.election_timer = self.generate_random_float()
        self.heartbeat_timer = None
        self.hearbeat_detection = False
        self.x = 0
        self.log_file = f'assignment/logs_node_{node_id}/logs.txt'
        self.metadata_file = f'assignment/logs_node_{node_id}/metadata.txt'
        self.dump_file = f'assignment/logs_node_{node_id}/dump.txt'
        self.lease_timer = 0
        self.new_leader_lease_check =0
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
            print("Inside Leader")
            response.data = "data"
            response.leaderId = str(self.leader_id)
            response.success = True
            return response

        print(self.parse_and_apply_command(request.request))
        response.data = "data"
        response.leaderId = str(self.leader_id)
        response.success = False
        return response

    def parse_and_apply_command(self, command_str):
        # Split the command string into tokens
        print("Parsing command")
        tokens = command_str.strip('{}').split()

        if tokens[0] == 'SET':
            # Parse SET command
            if len(tokens) != 3:
                return "SET command should have format: SET key value"
            key, value = tokens[1], tokens[2]
            self.log.append({'type': 'SET', 'key': key, 'value': value, 'term':self.current_term})
            print(self.log)
            self.write_to_log_file(f"SET {key} {value} {self.current_term}\n")  # Write to log file

            for current_id, peer_node in enumerate(self.peer_nodes, start=0):
                if current_id == self.node_id:
                    continue

                request = raft_pb2.AppendEntriesRequest()
                request.term = self.current_term
                request.leaderId = self.node_id
                if len(self.log) != 0:
                    request.prevLogIndex = len(self.log) - 1
                    request.prevLogTerm = int(self.log[-1].get('term'))
                else:
                    request.prevLogIndex = 0
                    request.prevLogTerm = 0
                request.leaderCommit = self.commit_index
                request.isHeartbeat = False
                entry = request.entries.add()
                entry.index = len(self.log)
                entry.term = self.current_term
                entry.data = f"SET {key} {value} {self.current_term}\n"

                try:
                    channel = grpc.insecure_channel(peer_node)
                    stub = raft_pb2_grpc.RaftNodeStub(channel)
                    response = stub.AppendEntries(request=request)
                    print(f"AppendEntries response from node {node_id}: {response}")
                except _InactiveRpcError:
                    print(f"The node at {peer_node} is offline")

            return "SET operation successful"

        elif tokens[0] == 'GET':
            # Parse GET command
            if len(tokens) != 2:
                return "GET command should have format: GET key"
            key = tokens[1]
            # Search the log for the latest value of the specified key
            latest_value = self.get_latest_value(key)
            return latest_value if latest_value is not None else "Key not found"

        else:
            return "Invalid command"

    def get_latest_value(self, key):
        # Search the log for the latest value of the specified key
        # Start from the end of the log to find the most recent SET operation for the key
        for entry in reversed(self.log):
            if entry['type'] == 'SET' and entry['key'] == key:
                return entry['value']
        return None  # Key not found in the log

    def write_to_log_file(self, content):
        # Write content to log file
        try:
            # Write content to log file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(content + '\n')
            print(f"Content '{content}' written to log file.")
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def fetch_log_lines(self):
        # List to store the fetched log lines as strings
        log_lines = []

        try:
            # Open the log file in read mode
            with open(self.log_file, 'r') as file:
                # Read each line from the file
                for line in file:
                    # Strip any leading or trailing whitespace characters
                    line = line.strip()
                    # Append the line to the list
                    log_lines.append(line)
                    tokens = line.strip('{}').split()
                    if(tokens[0]=="SET"):
                        key, value, term = tokens[1], tokens[2], tokens[3]
                        self.log.append({'type': 'SET', 'key': key, 'value': value, 'term': term})
                    
        except FileNotFoundError:
            print(f"Error: File '{self.log_file}' not found.")
        except Exception as e:
            print(f"Error occurred while reading file '{self.log_file}': {e}")

    def write_to_dump_file(self, message):
        with open(self.dump_file, 'a') as dump_file:
            dump_file.write(f"{message}\n")


    def AppendEntries(self, request, context):

        if request.isHeartbeat:
            # The current request is just a heartbeat
            self.x = 0
            self.leader_id=request.leaderId
            self.new_leader_lease_check=request.leaderLeaseDuration
            return raft_pb2.AppendEntriesResponse(term=self.current_term, success=True)

        if request.term < self.current_term:
            return raft_pb2.AppendEntriesResponse(term=self.current_term, success=False)

        if len(self.log) < request.prevLogIndex or (
                len(self.log) > 0 and self.log[request.prevLogIndex - 1].term != request.prevLogTerm):
            return raft_pb2.AppendEntriesResponse(term=self.current_term, success=False)

        # Step 3: If an existing entry conflicts with a new one, delete the existing entry and all that follow it
        # This step can be omitted if you handle log consistency elsewhere
        if len(request.entries) > 0:
            for entry in request.entries:
                if entry.index <= len(self.log):
                    if self.log[entry.index - 1].term != entry.term:
                        # Conflict found, delete existing entry and all that follow it
                        del self.log[entry.index - 1:]
                        break

        # Append new entries to the log
        for entry in request.entries:
            if entry.index > len(self.log):
                self.log.append(entry)
            else:
                self.log[entry.index - 1] = entry

        # Update commit index if necessary
        if request.leaderCommit > self.commit_index:
            self.commit_index = min(request.leaderCommit, len(self.log))

        # Update current term
        self.current_term = request.term

        return raft_pb2.AppendEntriesResponse(term=self.current_term, success=True)

    def RequestVote(self, request, context):
        response = raft_pb2.RequestVoteResponse()
        response.term = self.current_term
        # response.voteGranted = True
        # return response

        # Check if the candidate's term is less than the current term
        # if request.term < self.current_term:
        #     print(f"Sending False for terms {request.term} {self.current_term}")
        #     response.voteGranted = False
        #     return response

        # Check if the node has already voted for a candidate in this term

        print(self.voted_for)
        print(request.candidateId)

        if self.voted_for == -1 or self.voted_for == request.candidateId:
            print("Checking condition")
            print("hello",self.log)
            
            if (len(self.log)==0) or (request.lastLogTerm >= self.log[-1].get("term")) or   \
                    (request.lastLogTerm == self.log[-1].get("term") and request.lastLogIndex >= len(self.log) - 1) :
                print("Inner Condition")
                response.voteGranted = True
                self.voted_for = request.candidateId
                self.write_metadata()
                return response

        # If the conditions are not met, do not grant the vote
        response.voteGranted = False
        return response
    
    def write_metadata(self):
        with open(self.metadata_file, 'w') as f:  # Use 'w' mode for write (overwrite)
            f.write(f"{self.current_term}\n{self.voted_for}\n")

    def read_metadata(self):
        try:
            with open(self.metadata_file, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    self.current_term = int(lines[0].strip())
                    self.voted_for = int(lines[1].strip())
                    print(f"Metadata read successfully: current_term={self.current_term}, voted_for={self.voted_for}")
                else:
                    print("Error: Metadata file does not have enough lines.")
        except FileNotFoundError:
            print(f"Error: Metadata file '{self.metadata_file}' not found.")
        except Exception as e:
            print(f"Error reading metadata file: {e}")
            

    def start(self):
        time.sleep(10)
        # Start the node's main loop in a separate thread
        # Thread(target=self.run).start()
        self.run()

    def run(self):
        print(f"Node {self.node_id} is running and active.")
        self.fetch_log_lines()
        self.read_metadata()

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

        self.follower_behavior()
        Thread(target=self.hearbeat_sensor).start()
        self.create_node_files(self.node_id)



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
        self.current_term+=1

        # Prepare the RequestVoteRequest message
        request = raft_pb2.RequestVoteRequest()
        request.term = self.current_term
        request.candidateId = self.node_id

        if len(self.log) != 0:
            print("Inside condition for log")
            request.lastLogIndex = len(self.log) - 1 
            request.lastLogTerm = int(self.log[-1].get("term"))
        else:
            request.lastLogIndex = 0
            request.lastLogTerm = 0

        # Send the request to each peer node and gather responses
        votes_received = 1  # Counting self vote
        for node_id, peer_node in enumerate(self.peer_nodes, start=0):
            if node_id == self.node_id:
                continue

            response = self.request_vote(peer_node, request)
            if response:
                votes_received += 1

        self.voted_for = self.node_id
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
            return response.voteGranted
        except _InactiveRpcError:
            print(f"The node at {peer_node} is offline")
            return False

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
        print(int(time.time()-self.new_leader_lease_check))
        #time.sleep(time.time()-self.new_leader_lease_check)
        print(f"Node {self.node_id} is the leader")
        self.write_to_log_file("NO OP 0")
        self.leader_id = self.node_id
        self.current_term += 1
        self.write_metadata()
        Thread(target=self.send_heartbeats()).start()
        Thread(target=self.lease_checker()).start()

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
        elif term >= self.current_term & self.voted_for == -1:
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
            if self.state != "leader":
                sys.exit()
                break

            # Send heartbeats to followers
            request = raft_pb2.AppendEntriesRequest()
            request.term = self.current_term
            request.leaderId = self.node_id
            # request.prevLogIndex = len(self.log) - 1 if self.log else 0  # Index of the last log entry
            # print("Prtining prev log", self.log[-1])
            # request.prevLogTerm = self.log[-1].get('term') if self.log else 0  # Term of the last log entry

            if len(self.log) != 0:
                print("Inside condition for log")
                print(self.log)

                request.prevLogIndex = len(self.log) - 1
                request.prevLogTerm = int(self.log[-1].get('term'))
            else:
                request.prevLogIndex = 0
                request.prevLogTerm = 0

            request.leaderCommit = self.commit_index  # Index of highest log entry known to be committed
            request.leaderLeaseDuration = time.time()
            request.isHeartbeat = True
            count=0

            for node_id, peer_node in enumerate(self.peer_nodes, start=0):
                if node_id == self.node_id:
                    continue

                print(peer_node)
                try:
                    channel = grpc.insecure_channel(peer_node)
                    stub = raft_pb2_grpc.RaftNodeStub(channel)
                    response = stub.AppendEntries(request=request)
                    if response.success:
                        count+=1
                    print(f"Got response: {response}")
                except _InactiveRpcError:
                    print(f"The node at {peer_node} is offline")

                time.sleep(1)
            if(count>=len(peer_nodes)/2):
                self.lease_timer=0

    def lease_checker(self):
        
        while True:
            if(self.state!="leader"):
                sys.exit()
                break
            if(self.lease_timer==1):
                self.follower_behavior()
                self.state = "follower"

            self.lease_timer = self.lease_timer+1
            time.sleep(self.lease_duration)
        

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
    try:
        if len(sys.argv) != 2:
            print("Usage: python filename.py <node_id>")
            sys.exit(1)

        node_id = int(sys.argv[1])
        peer_nodes = ["localhost:50589", "localhost:50590", "localhost:55591"]

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
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting...")
        node.state = "follower"
        # Perform cleanup operations here if necessary
        sys.exit(0)
