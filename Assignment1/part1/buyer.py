import uuid
import grpc
import task_pb2
import task_pb2_grpc
from datetime import datetime
from concurrent import futures
import argparse

class Buyer(task_pb2_grpc.MarketServicer):
    
    def __init__(self, port):
        self.port = port
        self.addr = "10.128.0.4"
        self.unique_id = str(uuid.uuid1())
        self.item_list = {}
        self.channel = grpc.insecure_channel("34.133.227.248:50051")
        self.stub = task_pb2_grpc.MarketStub(self.channel)

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        task_pb2_grpc.add_MarketServicer_to_server(self, server=server)
        server.add_insecure_port(f"[::]:{self.port}")
        server.start()
        print(f"{self.get_current_time()} Notification server for buyer started. Listening on port {self.port}")
        self.server = server

    def stop_server(self):
        self.server.stop(None)
    
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

    def get_current_time(self):
        now = datetime.now()
        formatted_time = now.strftime("[%d:%m:%Y %H:%M:%S]")
        return formatted_time

    def search_item(self):
        name = input("Enter the item name (leave blank to skip): ")
        category = input("Enter the item category (0 for Electronics, 1 for Fashion, 2 for Others): ")
        
        request = task_pb2.BuyerSearchItemRequest(
            name=name,
            category=category
        )

        response = self.stub.SearchItem(request)
        
        if response.status == task_pb2.BuyerSearchItemResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} Searching successful. Printing results")
            print(response)
        else:
            print(f"{self.get_current_time()} Search failed. Reason: {response.message}")


    def buy_item(self):
        item_id = int(input("Enter the item ID: "))
        quantity = int(input("Enter the quantity: "))
        
        request = task_pb2.BuyItemRequest(
            item_id=item_id,
            quantity=quantity,
            buyer_address=f"{self.addr}:{self.port}"
        )

        response = self.stub.BuyItem(request)

        if response.status == task_pb2.BuyItemResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} SUCCESS: Item purchased successfully!")
        else:
            print(f"{self.get_current_time()} FAIL: {response.message}")



    def add_to_wishlist(self):
        item_id = int(input("Enter item ID you want to wishlist"))
        request = task_pb2.AddToWishListRequest(
            item_id=item_id,
            buyer_address=f"{self.addr}:{self.port}"
        )

        response = self.stub.AddToWishList(request)

        if response.status == task_pb2.AddToWishListResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} SUCCESS: Item added to wishlist successfully!")
        else:
            print(f"{self.get_current_time()} FAIL: {response.message}")


    def rate_item(self):
        item_id = int(input("Enter item ID you want to wishlist: "))
        rating = int(input("Enter rating (1-5): "))
        request = task_pb2.RateItemRequest(
            item_id=item_id,
            buyer_address=f"{self.addr}:{self.port}",
            rating=rating
        )

        response = self.stub.RateItem(request)

        if response.status == task_pb2.RateItemResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} SUCCESS: Item rated successfully!")
        else:
            print(f"{self.get_current_time()} FAIL: {response.message}")

def print_menu():
    print("-"*50)
    print("1. Search Item")
    print("2. Buy Item")
    print("3. Add to Wishlist")
    print("4. Rate Item")
    print("-"*50)
    print("What would you like to do?")
    print("-"*50)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Add port")
    
    args = parser.parse_args()

    port = args.port 
    buyer = Buyer(port=port)
    buyer.serve()

    while True:
        print_menu()
        task = input("")
        if task == "1":
            buyer.search_item()
        elif task == "2":
            buyer.buy_item()
        elif task == "3":
            buyer.add_to_wishlist()
        elif task == "4":
            buyer.rate_item()
        else:
            print("Invalid input. Please enter from the list")

if __name__ == "__main__":
    main()
