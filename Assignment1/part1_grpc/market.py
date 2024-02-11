from concurrent import futures
from datetime import datetime

import grpc
import task_pb2
import task_pb2_grpc

class Market(task_pb2_grpc.MarketServicer):

    seller_list = {}
    item_list = {}

    def __init__(self, port):
        self.port = port

    def RegisterSeller(self, request, context):
        print(f"{self.get_current_time()} Received registration request from {request.ip_port}, uuid = {request.uuid}")
        
        if request.uuid not in self.seller_list:
            response = task_pb2.RegisterSellerResponse(status=task_pb2.RegisterSellerResponse.Status.SUCCESS)
            self.seller_list[request.uuid] = request.ip_port
        else:
            response = task_pb2.RegisterSellerResponse(status=task_pb2.RegisterSellerResponse.Status.FAILED)
        return response

    def SellItem(self, request, context):

        uuid = request.seller_uuid
        
        if uuid not in self.seller_list:
            response = task_pb2.SellItemResponse(
                status = task_pb2.SellItemResponse.Status.FAILED,
                message = "Seller not registered",
                item_id = -1
            )

            return response
        
        print(f"{self.get_current_time()} Received sell item request from {self.seller_list[uuid]}, uuid = {uuid}")

        item_id = len(self.item_list) + 1
        
        self.item_list[item_id] = {
            "name" : request.product_name,
            "category" : request.category,
            "quantity" : request.quantity,
            "description" : request.description,
            "price" : request.price_per_unit,
            "uid" : request.seller_uuid
        }

        # self.item_list[item_id] = request

        print(self.item_list)
        response = task_pb2.SellItemResponse(
                status=task_pb2.SellItemResponse.Status.SUCCESS,
                message = f"Item added successfully with id {item_id}",
                item_id=item_id
            )
        
        return response

    def get_current_time(self):
        now = datetime.now()
        formatted_time = now.strftime("[%d:%m:%Y %H:%M:%S]")
        return formatted_time

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        task_pb2_grpc.add_MarketServicer_to_server(self, server=server)
        server.add_insecure_port(f"localhost:{self.port}")
        server.start()
        print(f"{self.get_current_time()} Market server started. Listening on port {self.port}")
        server.wait_for_termination()

if __name__ == "__main__":
    market = Market(port=50051)
    market.serve()
