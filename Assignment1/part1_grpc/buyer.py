import uuid
import grpc
import task_pb2
import task_pb2_grpc
from datetime import datetime

class Buyer:
    
    def __init__(self, port):
        self.port = port
        self.addr = "localhost"
        self.unique_id = str(uuid.uuid1())
        self.item_list = {}
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = task_pb2_grpc.MarketStub(self.channel)

    
    def get_current_time(self):
        now = datetime.now()
        formatted_time = now.strftime("[%d:%m:%Y %H:%M:%S]")
        return formatted_time

    def search_item(self):
        request = task_pb2.BuyerSearchItemRequest(
            name = "",
            category = "2"
        )

        response = self.stub.SearchItem(request)
        
        if response.status == task_pb2.BuyerSearchItemResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} Searching successful. Printing results")
            print(response)
        else:
            print(f"{self.get_current_time()} Search failed. Reason: {response.message}")

    def buy_item(self):
        pass

    def add_to_wishlist(self):
        pass

    def rate_item(self):
        pass


def main():
    port = 50053
    buyer = Buyer(port=port)

    while True:
        print("-"*50)
        print("1. Search Item")
        print("2. Buy Item")
        print("3. Add to Wishlist")
        print("4. Rate Item")
        print("-"*50)
        task = input("What would you like to do?: ")

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
