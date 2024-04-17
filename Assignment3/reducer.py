import os
import grpc
from concurrent import futures
import argparse
import master_pb2 as pb2
import master_pb2_grpc as pb2_grpc
import random

class Reducer(pb2_grpc.MasterServicer):
    def __init__(self, id, port):
        self.reducer_id = id
        self.port = port
        self.centroids = None
        self.mapper_port_list = [50001, 50002, 50003]
        self.data_points_list = None
        self.updated_centroid = []

    def ReducerInput(self, request, context):
        choice = random.choice([True, False])
        if choice:
            centroid_id = request.centroid_id
            self.centroids = [request.centroids[0].x, request.centroids[0].y]
            response_list = self.shuffle_and_sort()
            data_points = []

            for reducer_data in response_list:
                if reducer_data:
                    data_point_strings = reducer_data.strip().split('\n')
                    reducer_data_points = []
                    for data_point_str in data_point_strings:
                        data_point = [float(coord) for coord in data_point_str.strip('[]').split(',')]
                        reducer_data_points.append(data_point)
                    data_points.append(reducer_data_points)
            
            flattened_data_points = [data_point for reducer_data_points in data_points for data_point in reducer_data_points]
            self.data_points_list = flattened_data_points

            self.reduce()
            return pb2.ReducerInputResponse(status=True, x=self.centroids[0], y=self.centroids[1])
        else:
            return pb2.ReducerInputResponse(status=False)

    def shuffle_and_sort(self):
        print("Suffling and Sorting")
        response_list = []
        for port in self.mapper_port_list:
            with grpc.insecure_channel(f'localhost:{port}') as channel:
                stub = pb2_grpc.MasterStub(channel)
                request = pb2.DataPointRequest(id=self.reducer_id)
                response = stub.RequestPartition(request)
                if response.status:
                    response_list.append(response.points)
                else:
                    print(f"Error in retrieving data from mapper with port {port}")

        return response_list

    def reduce(self):

        if self.data_points_list is None:
            print("Error: No data points to reduce.")
            return
    
        centroid = [sum(coord) / len(self.data_points_list) for coord in zip(*self.data_points_list)]
        file_path = f"data/reducers/reducer_{self.reducer_id}.txt"



        with open(file_path, "w") as file:
            file.write(f"Centroid ID: {self.reducer_id}, Centroid: {centroid}\n")

        self.updated_centroid = centroid

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_MasterServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        server.start()
        print(f"Started Reducer {self.reducer_id}. Listening on port {self.port}")
        server.wait_for_termination()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Mapper.')
    parser.add_argument('--id', type=int, required=True, help='Mapper ID')
    parser.add_argument('--port', type=int, required=True, help='Port number')
    args = parser.parse_args()

    reducer = Reducer(id=args.id, port=args.port)
    reducer.serve()
