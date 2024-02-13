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
            "uid" : request.seller_uuid,
            "rating" : 0
        }

        print(self.item_list)
        response = task_pb2.SellItemResponse(
                status=task_pb2.SellItemResponse.Status.SUCCESS,
                message = f"Item added successfully with id {item_id}",
                item_id=item_id
            )
        
        return response
    
    def UpdateItem(self, request, context):
        uuid = request.seller_uuid
        if uuid not in self.seller_list:
            response = task_pb2.UpdateItemResponse(
                status = task_pb2.UpdateItemResponse.Status.FAILED,
                message = "Seller not registered"
            )

            return response
        
        item_id = request.item_id
        print(f"{self.get_current_time()} Recieved update item {item_id} request from {self.seller_list[uuid]}")
        if item_id not in self.item_list:
            response = task_pb2.UpdateItemResponse(
                status = task_pb2.UpdateItemResponse.Status.FAILED,
                message = "No item registered with corresponding ID"
            )

            return response

        if self.item_list[item_id]["uid"] == request.seller_uuid:
            print("Before:", self.item_list[item_id])

            self.item_list[item_id]["price"] = request.new_price
            self.item_list[item_id]["quantity"] = request.new_quantity
        
            print("After:", self.item_list[item_id])

            response = task_pb2.UpdateItemResponse(
                status = task_pb2.UpdateItemResponse.SUCCESS,
                message = "Item updated successfully!"
            )

            return response
        else:
            response = task_pb2.UpdateItemResponse(
                status = task_pb2.UpdateItemResponse.Status.FAILED,
                message = "Given item ID not registered with the corresponding UID"
            )
            return response

    def DeleteItem(self, request, context):
        uuid = request.seller_uuid
        if uuid not in self.seller_list:
            response = task_pb2.DeleteItemResponse(
                status=task_pb2.DeleteItemResponse.Status.FAILED,
                message="Seller not registered"
            )
            return response
        
        item_id = request.item_id
        print(f"{self.get_current_time()} Received delete item {item_id} request from {self.seller_list[uuid]}")
        if item_id not in self.item_list:
            response = task_pb2.DeleteItemResponse(
                status=task_pb2.DeleteItemResponse.Status.FAILED,
                message="No item registered with corresponding ID"
            )
            return response

        if self.item_list[item_id]["uid"] == request.seller_uuid:
            print(f"Deleting item {item_id}")
            del self.item_list[item_id]
            response = task_pb2.DeleteItemResponse(
                status=task_pb2.DeleteItemResponse.Status.SUCCESS,
                message="Item deleted successfully!"
            )
            return response
        else:
            response = task_pb2.DeleteItemResponse(
                status=task_pb2.DeleteItemResponse.Status.FAILED,
                message="Given item ID not registered with the corresponding UID"
            )
            return response

    def DisplaySellerItems(self, request, context):
        seller_uuid = request.seller_uuid
        seller_address = request.seller_address

        if seller_uuid not in self.seller_list:
            print("Seller not registered")

        seller_items = []
        
        for item_id, item in self.item_list.items():

            if item["uid"] == seller_uuid:
                seller_item = task_pb2.SellerItem(
                    item_id = item_id,
                    price = item["price"],
                    product_name = item["name"],
                    category = str(item["category"]),
                    description = item["description"],
                    quantity_remaining = item["quantity"],
                    seller_address = self.seller_list[seller_uuid],
                    rating = item["rating"]
                )
                seller_items.append(seller_item)

        
        print("Printing seller items", seller_items)
        response = task_pb2.DisplaySellerItemsResponse(
            status=task_pb2.DisplaySellerItemsResponse.Status.SUCCESS,
            message="Completed successfully!",
            items=seller_items
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
