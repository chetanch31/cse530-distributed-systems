import os
import grpc
from concurrent import futures
import master_pb2 as pb2
import master_pb2_grpc as pb2_grpc
import argparse
import random

class Mapper(pb2_grpc.MasterServicer):
    
    def __init__(self, port, id):
        self.mapper_id = id
        self.port = port
        self.input_split = []
        self.centroids = []
        self.output_dir = "data\mappers\m" + str(self.mapper_id)
        self.file_path = "data\input\points.txt"

    def MapperInput(self, request, context):
        # Extracting data points
        data_point_indc = [request.data_points[0].x, request.data_points[0].y]
        current_data_points = self.read_and_parse_points(data_point_indc)
        self.input_split = current_data_points

        # Extracting centroids
        centroid_values = []
        for centroid in request.centroids:
            centroid_values.append([centroid.x, centroid.y])
        self.centroids = centroid_values

        choice = random.choice([True, False])
        if choice:
            self.run_mapper()
            return pb2.MapperInputResponse(status=True)
        else:
            return pb2.MapperInputResponse(status=False)


    def RequestPartition(self, request, context):
        request_id = request.id
        file_name = os.path.join(self.output_dir, f'partition_{request_id}.txt')
        read_str = ""
        print(request_id)
        print("File: ", file_name)

        with open(file_name, "r") as file:
            read_str = file.read()

        return pb2.DataPointResponse(points=read_str, status=True)
        

    def read_and_parse_points(self, index_list):
        data_points = []
        with open(self.file_path, 'r') as file:
            for line in file:
                x, y = map(float, line.strip().split(','))
                data_points.append([x, y])
        return data_points[index_list[0]:index_list[1]+1]

    def k_means_map(self, x):
    
        distances = [((x[0] - mean[0]) ** 2 + (x[1] - mean[1]) ** 2) ** 0.5 for mean in self.centroids]
        min_distance_index = distances.index(min(distances))
        return min_distance_index, x

    def run_mapper(self):

        intermediate_key_value_pairs = []
        for data_point in self.input_split:
            key, value = self.k_means_map(data_point)
            intermediate_key_value_pairs.append((key, value))
        
        print(intermediate_key_value_pairs)
        partitions = self.partition(intermediate_key_value_pairs, num_reducers=3)
        self.write_partitions(partitions)

    def partition(self, key_value_pairs, num_reducers):
        partitions = [[] for _ in range(num_reducers)]
        for key, value in key_value_pairs:
            partition_index = key % num_reducers
            partitions[partition_index].append((key, value))

        return partitions

    def write_partitions(self, partitions):
        print("Writing to files")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        for i, partition in enumerate(partitions):
            output_file = os.path.join(self.output_dir, f'partition_{i}.txt')
            with open(output_file, 'w') as f:
                for key, value in partition:
                    f.write(f"{value}\n")

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_MasterServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        server.start()
        print(f"Started Mapper {self.mapper_id}. Listening on port {self.port}")
        server.wait_for_termination()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Mapper.')
    parser.add_argument('--id', type=int, required=True, help='Mapper ID')
    parser.add_argument('--port', type=int, required=True, help='Port number')
    args = parser.parse_args()

    mapper = Mapper(id=args.id, port=args.port)
    mapper.serve()
