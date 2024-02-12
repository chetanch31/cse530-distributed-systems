import uuid
import grpc
import task_pb2
import task_pb2_grpc
from datetime import datetime

class Seller:

    def __init__(self, port):
        self.port = port
        self.addr = "localhost"
        self.unique_id = str(uuid.uuid1())
        self.item_list = {}
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = task_pb2_grpc.MarketStub(self.channel)

    def register_seller(self):
        request = task_pb2.RegisterSellerRequest(
            ip_port=f"localhost:{self.port}",
            uuid=self.unique_id
        )
        response = self.stub.RegisterSeller(request)
        if response.status == task_pb2.RegisterSellerResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} Seller registration successful!")
        else:
            print(f"{self.get_current_time()} Seller registration failed!")

    def sell_item(self):

        # TODO take request input from the user

        request = task_pb2.SellItemRequest(
            product_name="Smartphone",
            category=task_pb2.ProductCategory.ELECTRONICS,
            quantity=10,
            description="A high-quality smartphone",
            seller_address=self.addr,
            seller_uuid=self.unique_id,
            price_per_unit=500.0
        )
        response = self.stub.SellItem(request)
        if response.status == task_pb2.SellItemResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} Success! Item ID: {response.item_id}")
            self.item_list[response.item_id] = request
        else:
            print(f"{self.get_current_time()} Failed! Reason: {response.message}")

    def update_item(self):
        # TODO update request to take input from user
        request = task_pb2.UpdateItemRequest(
            item_id = 1,
            new_price = 2000,
            new_quantity = 20,
            seller_address = self.addr,
            seller_uuid = self.unique_id
        )
        
        response = self.stub.UpdateItem(request)

        if response.status == task_pb2.UpdateItemResponse.Status.SUCCESS:
            print(f"{self.get_current_time()} Success! {response.message}")
        else:
            print(f"{self.get_current_time()} Failed! Reason: {response.message}")

    def delete_item(self):
        item_id = 2
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
            print(f"{self.get_current_time()} Failed! Reason: {response.status}")



    def get_current_time(self):
        now = datetime.now()
        formatted_time = now.strftime("[%d:%m:%Y %H:%M:%S]")
        return formatted_time


def main():
    port = 50052
    seller = Seller(port=port)

    while True:
        print("-"*50)
        print("1. Register Seller")
        print("2. Sell Item")
        print("3. Update Item")
        print("4. Delete Item")
        print("5. Display Seller Items")
        print("-"*50)
        task = input("What would you like to do (enter 1 or 2)?: ")

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
