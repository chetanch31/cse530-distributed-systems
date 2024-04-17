import os
import grpc
import numpy as np
from concurrent import futures
import argparse
import master_pb2
import master_pb2_grpc
import random
import time
from datetime import datetime

class Master():
    def __init__(self, num_mappers, num_reducers, num_centroids, num_iterations, file_path):
        self.num_mappers = num_mappers
        self.num_reducers = num_reducers
        self.num_centroids = num_centroids
        self.num_iterations = num_iterations

        self.port_list = [50001, 50002, 50003]
        
        self.file_path = file_path
        self.data_points = self.read_input_file(file_path)
        self.total_points = len(self.data_points)
        self.indices_chunks = self.divide_indices(self.total_points, self.num_mappers)

        self.centroids = None

    def run(self):
        self.centroids = self.initialize_centroids()
        print("Random centroids: ", self.centroids)

        print(self.indices_chunks)
        self.run_mappers()
        # for iteration in range(self.num_iterations):
        #     self.run_mappers()
        #     self.run_reducers()
        #     self.centroids = self.centroid_compilation()

        #     print(f"Iteration {iteration}: Centroids = {self.centroids}")

        #     if self.check_convergence():
        #         break
    
    
    def read_input_file(self, file_path):
        data_points = []
        with open(file_path, 'r') as file:
            for line in file:
                x, y = map(float, line.strip().split(','))
                data_points.append((x, y))
        return data_points

    def divide_indices(self, total_points, num_mappers):
        chunk_size = total_points // num_mappers
        indices_chunks = []
        start_index = 0
        for i in range(num_mappers):
            end_index = start_index + chunk_size - 1 if i < num_mappers - 1 else total_points - 1
            indices_chunks.append((start_index, end_index))
            start_index = end_index + 1
        return indices_chunks

    def initialize_centroids(self):
        return [[random.random(), random.random()] for _ in range(self.num_centroids)]

    def run_mappers(self):
        with futures.ThreadPoolExecutor() as executor:
            mapper_futures = []
            for mapper_id, port in enumerate(self.port_list):
                mapper_future = executor.submit(self.initialize_mapper, mapper_id, port)
                mapper_futures.append(mapper_future)
            
            for future in mapper_futures:
                future.result()

    def initialize_mapper(self, mapper_id, port):
        while True:
            with grpc.insecure_channel(f'localhost:{port}') as channel:
                stub = master_pb2_grpc.MasterStub(channel=channel)

                request = master_pb2.MapperInputRequest()

                tuple_data_point1 = request.data_points.add()
                tuple_data_point1.x = self.indices_chunks[mapper_id][0]
                tuple_data_point1.y = self.indices_chunks[mapper_id][1]

                for centroid_values in self.centroids:
                    centroid = request.centroids.add()
                    centroid.x = centroid_values[0]
                    centroid.y = centroid_values[1]

                response = stub.MapperInput(request)
                print(response)
                
                if response.status:
                    print(f"{self.get_current_time()} Mapper {mapper_id} returned True.")
                    break  
                else:
                    print(f"{self.get_current_time()} Mapper {mapper_id} returned False: Retrying")
                    time.sleep(2) 

    def run_reducers(self):
        for reducer_id in range(self.num_reducers):
            self.initialize_reducer(reducer_id)

    def centroid_compilation(self):
        new_centroids = []
        for reducer_id in range(self.num_reducers):
            new_centroids.extend(self.get_centroids_from_reducer(reducer_id))
        return np.array(new_centroids)

    def check_convergence(self):
        return False




    # def initialize_reducer(self, reducer_id):
    #     with grpc.insecure_channel(f'localhost:{reducer_id+50052}') as channel:
    #         stub = ReducerServicer_pb2_grpc.ReducerServicer_Stub(channel)
    #         request = InitializeReducerRequest(reducer_id=reducer_id)
    #         response = stub.initialize_reducer(request)
    #         if response.status != 'SUCCESS':
    #             # Handle reducer failure and reassign the task
                # pass

    # def get_centroids_from_reducer(self, reducer_id):
    #     with grpc.insecure_channel(f'localhost:{reducer_id+50052}') as channel:
    #         stub = ReducerServicer_pb2_grpc.ReducerServicer_Stub(channel)
    #         request = CentroidCompilationRequest(reducer_id=reducer_id)
    #         response = stub.get_centroids(request)
    #         return response.centroids

    def get_current_time(self):
        now = datetime.now()
        formatted_time = now.strftime("[%d:%m:%Y %H:%M:%S]")
        return formatted_time

def main():
    num_mappers = 3
    num_reducers = 2
    num_centroids = 2
    num_iterations = 3

    file_path = "data\input\points.txt"

    master = Master(num_mappers, num_reducers, num_centroids, num_iterations, file_path)
    master.run()

if __name__ == '__main__':
    main()
