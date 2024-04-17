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
import threading

class Master():
    def __init__(self, num_mappers, num_reducers, num_centroids, num_iterations, file_path):
        self.num_mappers = num_mappers
        self.num_reducers = num_reducers
        self.num_centroids = num_centroids
        self.num_iterations = num_iterations

        self.mapper_port_list = [50001, 50002, 50003]
        self.reducer_port_list = [60001, 60002, 60003]
        
        self.file_path = file_path
        self.data_points = self.read_input_file(file_path)
        self.total_points = len(self.data_points)
        self.indices_chunks = self.divide_indices(self.total_points, self.num_mappers)
        
        self.mapper_done_event = threading.Event()
        self.reducer_done_event = threading.Event()
        self.centroids = None
        self.previous_centroids = None

        self.append_to_file("Master intiated")

    def run(self):
        self.centroids = self.initialize_centroids()
        print("Random centroids: ", self.centroids)
        self.append_to_file(f"Random centroid values: {self.centroids}")

        for iteration in range(self.num_iterations):
            self.run_mappers()
            self.mapper_done_event.wait()
            self.run_reducers()
            self.reducer_done_event.wait()

            self.append_to_file(f"Iteration {iteration}: Centroids = {self.centroids}")

            if self.check_convergence():
                self.append_to_file("Reached Convergence")
                break

        with open("data/centroids.txt", "w") as file:
            file.write(str(self.centroids))
    
    
    def read_input_file(self, file_path):
        data_points = []
        with open(file_path, 'r') as file:
            for line in file:
                x, y = map(float, line.strip().split(','))
                data_points.append((x, y))
        return data_points

    def divide_indices(self, total_points, num_mappers):
        self.append_to_file("Divinding indices")
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
            for mapper_id, port in enumerate(self.mapper_port_list):
                mapper_future = executor.submit(self.initialize_mapper, mapper_id, port)
                mapper_futures.append(mapper_future)
            
            for future in mapper_futures:
                future.result()
        self.mapper_done_event.set()

    def initialize_mapper(self, mapper_id, port):
        while True:
            try:
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
                        self.append_to_file(f"Mapper {mapper_id} returned True.")
                        break  
                    else:
                        self.append_to_file(f"Mapper {mapper_id} returned False: Retrying")
                        time.sleep(2)
                        
            except grpc.RpcError as e:
                print(f"{mapper_id} encountered an error: {e}. Retrying in 5 seconds.")
                self.append_to_file(f"Mapper {mapper_id} encountered an error: {e}. Retrying in 5 seconds.")
                time.sleep(5)


    def run_reducers(self):
        with futures.ThreadPoolExecutor() as executor:
            reducer_futures = []
            for reducer_id, port in enumerate(self.reducer_port_list):
                reducer_future = executor.submit(self.initialize_reducer, reducer_id, port)
                reducer_futures.append(reducer_future)
            
            for future in reducer_futures:
                future.result()

        self.reducer_done_event.set()

    def initialize_reducer(self, reducer_id, port):
        while True:
            try:
                with grpc.insecure_channel(f'localhost:{port}') as channel:
                    stub = master_pb2_grpc.MasterStub(channel=channel)

                    request = master_pb2.ReducerInputRequest(centroid_id=reducer_id)

                    centroid = request.centroids.add()
                    centroid.x = self.centroids[reducer_id][0]
                    centroid.y = self.centroids[reducer_id][1]

                    response = stub.ReducerInput(request)
                    print(response)

                    if response.status:
                        self.append_to_file(f"Reducer {reducer_id} returned True.")
                        new_centroids = [response.x, response.y]
                        self.centroids[reducer_id] = new_centroids
                        self.append_to_file(f"Received Centroids: {new_centroids} from reducer {reducer_id}")
                        break  
                    else:
                        self.append_to_file(f"Reducer {reducer_id} returned False: Retrying")
                        time.sleep(2)
            except grpc.RpcError as e:
                self.append_to_file(f"Reducer {reducer_id} encountered an error: {e}. Retrying in 5 seconds.")
                time.sleep(5)


    def check_convergence(self):
        if self.centroids is None:
            return False  

        threshold = 0.001  
        if self.previous_centroids is not None:
            for i in range(len(self.centroids)):
                distance = np.linalg.norm(np.array(self.centroids[i]) - np.array(self.previous_centroids[i]))
                if distance > threshold:
                    return False  

        
        self.previous_centroids = self.centroids
        return False

    def append_to_file(self, string_to_append):
        file_path = "dumb.txt"
        with open(file_path, "a") as file:
            file.write(self.get_current_time() +":" + string_to_append + "\n")

    def get_current_time(self):
        now = datetime.now()
        formatted_time = now.strftime("[%d:%m:%Y %H:%M:%S]")
        return formatted_time

def main():
    num_mappers = 3
    num_reducers = 3
    num_centroids = 3
    num_iterations = 5

    file_path = "data\input\points.txt"

    master = Master(num_mappers, num_reducers, num_centroids, num_iterations, file_path)
    master.run()

if __name__ == '__main__':
    main()
