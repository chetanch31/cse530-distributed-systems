import os
import grpc
from concurrent import futures
from protos.master_pb2 import InitializeReducerRequest, InitializeReducerResponse, CentroidCompilationRequest, CentroidCompilationResponse
from protos.master_pb2_grpc import ReducerServicer, add_ReducerServicer_to_server

class Reducer(ReducerServicer):
    def __init__(self, reducer_id):
        self.reducer_id = reducer_id
        self.centroids = None

    def initialize_reducer(self, request, context):
        self.reducer_id = request.reducer_id
        try:
            self.shuffle_and_sort()
            self.reduce()
            return InitializeReducerResponse(status='SUCCESS')
        except Exception as e:
            return InitializeReducerResponse(status='FAILURE')

    def shuffle_and_sort(self):
        # Implement the shuffle and sort logic
        pass

    def reduce(self):
        # Implement the reduce function to calculate new centroids
        pass

    def get_centroids(self, request, context):
        return CentroidCompilationResponse(centroids=self.centroids)

    def start(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_ReducerServicer_to_server(self, server)
        server.add_insecure_port(f'localhost:{self.reducer_id+50052}')
        server.start()
        print(f"Reducer {self.reducer_id} started")

    def terminate(self):
        # Terminate the reducer process
        pass