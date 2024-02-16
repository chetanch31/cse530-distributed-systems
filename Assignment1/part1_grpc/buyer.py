import uuid
import grpc
import task_pb2
import task_pb2_grpc
from datetime import datetime
from concurrent import futures

class Buyer(task_pb2_grpc.MarketServicer):
    
    def __init__(self, port):
        self.port = port
        self.addr = "localhost"
        self.unique_id = str(uuid.uuid1())
        self.item_list = {}
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = task_pb2_grpc.MarketStub(self.channel)

    def serve(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        task_pb2_grpc.add_MarketServicer_to_server(self, server=server)
        server.add_insecure_port(f"localhost:{self.port}")
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
        request = task_pb2.BuyerSearchItemRequest(
            name = "",
            category = ""
        )

        response = self.stub.SearchItem(request)
        
        if response.status == task_pb2.BuyerSearchItemResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} Searching successful. Printing results")
            print(response)
        else:
            print(f"{self.get_current_time()} Search failed. Reason: {response.message}")

    def buy_item(self):
        request = task_pb2.BuyItemRequest(
            item_id=1,
            quantity=5,
            buyer_address=f"{self.addr}:{self.port}"
        )

        response = self.stub.BuyItem(request)

        if response.status == task_pb2.BuyItemResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} SUCCESS: Item purchased successfully!")
        else:
            print(f"{self.get_current_time()} FAIL: {response.message}")


    def add_to_wishlist(self):
        request = task_pb2.AddToWishListRequest(
            item_id=1,
            buyer_address=f"{self.addr}:{self.port}"
        )

        response = self.stub.AddToWishList(request)

        if response.status == task_pb2.AddToWishListResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} SUCCESS: Item added to wishlist successfully!")
        else:
            print(f"{self.get_current_time()} FAIL: {response.message}")


    def rate_item(self):
        request = task_pb2.RateItemRequest(
            item_id=2,
            buyer_address=f"{self.addr}:{self.port}",
            rating=4
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
    port = 50054
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
