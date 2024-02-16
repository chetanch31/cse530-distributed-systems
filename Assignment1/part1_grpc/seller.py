import uuid
import grpc
import task_pb2
import task_pb2_grpc
from datetime import datetime
from concurrent import futures
import argparse

class Seller(task_pb2_grpc.MarketServicer):

    def __init__(self, port):
        self.port = port
        self.addr = "10.128.0.3"
        self.unique_id = str(uuid.uuid1())
        self.item_list = {}
        self.channel = grpc.insecure_channel("34.133.227.248:50051")
        self.stub = task_pb2_grpc.MarketStub(self.channel)

    def register_seller(self):
        request = task_pb2.RegisterSellerRequest(
            ip_port=f"{self.addr}:{self.port}",
            uuid=self.unique_id
        )
        response = self.stub.RegisterSeller(request)
        if response.status == task_pb2.RegisterSellerResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} Seller registration successful!")
        else:
            print(f"{self.get_current_time()} Seller registration failed!")

    def SendNotification(self, request, context):
        message = request.message
        item = request.item
        print()
        print(message)
        print(item)
        response = task_pb2.NotificationResponse(
            status = "Recieved"
        )
        print_menu()
        return response

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        task_pb2_grpc.add_MarketServicer_to_server(self, server=server)
        server.add_insecure_port(f"localhost:{self.port}")
        server.start()
        print(f"{self.get_current_time()} Notification server for seller started. Listening on port {self.port}")
        self.server = server

    def stop_server(self):
        self.server.stop(None)
    

    def sell_item(self):
        print("Enter item details:")
        product_name = input("Product Name: ")
        
        # Provide a list of available categories
        print("Select category:")
        print("0. Electronics")
        print("1. Fashion")
        print("2. Others")
        category_input = input("Enter category number: ")
        
        # Convert the category input to the corresponding enum value
        category_map = {
            "0": task_pb2.ProductCategory.ELECTRONICS,
            "1": task_pb2.ProductCategory.FASHION,
            "2": task_pb2.ProductCategory.OTHERS
        }
        category = category_map.get(category_input, task_pb2.ProductCategory.OTHERS)
        
        quantity = int(input("Quantity: "))
        description = input("Description: ")
        price_per_unit = float(input("Price per Unit: "))

        request = task_pb2.SellItemRequest(
            product_name=product_name,
            category=category,
            quantity=quantity,
            description=description,
            seller_address=self.addr,
            seller_uuid=self.unique_id,
            price_per_unit=price_per_unit
        )

        response = self.stub.SellItem(request)
        if response.status == task_pb2.SellItemResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} Success! Item ID: {response.item_id}")
            self.item_list[response.item_id] = request
        else:
            print(f"{self.get_current_time()} Failed! Reason: {response.message}")


    def update_item(self):
        item_id = int(input("Enter Item ID to update: "))
        new_price = float(input("Enter New Price: "))
        new_quantity = int(input("Enter New Quantity: "))
        
        request = task_pb2.UpdateItemRequest(
            item_id=item_id,
            new_price=new_price,
            new_quantity=new_quantity,
            seller_address=self.addr,
            seller_uuid=self.unique_id
        )
        
        response = self.stub.UpdateItem(request)

        if response.status == task_pb2.UpdateItemResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} Success! {response.message}")
        else:
            print(f"{self.get_current_time()} Failed! Reason: {response.message}")


    def delete_item(self):
        item_id = int(input("Enter item id to delete"))
        request = task_pb2.DeleteItemRequest(
            seller_address=self.addr,
            seller_uuid=self.unique_id,
            item_id= item_id
        )
        response = self.stub.DeleteItem(request)

        if response.status == task_pb2.DeleteItemResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} Success! {response.message}")
            del self.item_list[item_id]
        else:
            print(f"{self.get_current_time()} Failed! Reason: {response.message}")

    def display_seller_items(self):
        request = task_pb2.DisplaySellerItemsRequest(
            seller_address=self.addr,
            seller_uuid=self.unique_id
        )

        response = self.stub.DisplaySellerItems(request)

        if response.status == task_pb2.DisplaySellerItemsResponse.Status.SUCCESS:
            print("Seller Items:")
            for item in response.items:
                print(f"Item ID: {item.item_id}")
                print(f"Price: ${item.price}")
                print(f"Product Name: {item.product_name}")
                print(f"Category: {item.category}")
                print(f"Description: {item.description}")
                print(f"Quantity Remaining: {item.quantity_remaining}")
                print(f"Seller Address: {item.seller_address}")
                print(f"Rating: {item.rating}")
                print()
        else:
            print(f"{self.get_current_time()} Failed! Reason: {response.items}")



    def get_current_time(self):
        now = datetime.now()
        formatted_time = now.strftime("[%d:%m:%Y %H:%M:%S]")
        return formatted_time

def print_menu():
    print("-"*50)
    print("1. Register Seller")
    print("2. Sell Item")
    print("3. Update Item")
    print("4. Delete Item")
    print("5. Display Seller Items")
    print("-"*50)
    print("What would you like to do?:")
    print("-"*50)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Add port")
    
    args = parser.parse_args()

    port = args.port
    seller = Seller(port=port)
    seller.serve()

    while True:
        print_menu()
        task = input()
        if task == "1":
            seller.register_seller()
        elif task == "2":
            seller.sell_item()
        elif task == "3":
            seller.update_item()
        elif task == "4":
            seller.delete_item()
        elif task == "5":
            seller.display_seller_items()
        else:
            print("Invalid input. Please enter from the list")

if __name__ == "__main__":
    main()
