import uuid
import grpc
import task_pb2
import task_pb2_grpc
from datetime import datetime

def get_current_time():
    now = datetime.now()
    formatted_time = now.strftime("[%d:%m:%Y %H:%M:%S]")

    return formatted_time


def run(port, uid):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = task_pb2_grpc.MarketStub(channel=channel)

        while True:
            print("-"*50)
            print("1. Register Seller")
            print("2. Sell Item")
            print("-"*50)
            task = int(input("What would you like to do?: "))


            if task == 1:
                request = task_pb2.RegisterSellerRequest(
                    ip_port = f"localhost:{port}",
                    uuid = uid
                )

                response = stub.RegisterSeller(request)
                if response.status == task_pb2.RegisterSellerResponse.Status.SUCCESS:
                    print(f"{get_current_time()} Seller registration successful!")
                else:
                    print(f"{get_current_time()} Seller registration failed!")

            elif task == 2:
                print("Sell an item")
                request = task_pb2.SellItemRequest(
                    product_name="Smartphone",
                    category=task_pb2.ProductCategory.ELECTRONICS,
                    quantity=10,
                    description="A high-quality smartphone",
                    seller_address="localhost",
                    seller_uuid=unique_id,
                    price_per_unit=500.0
                )
                print(request)
                response = stub.SellItem(request)
                if response.status == task_pb2.SellItemResponse.Status.SUCCESS:
                    print(f"{get_current_time()} Item id: {response.item_id}")
                else:
                    print(f"{get_current_time()} Failed! Reason: {response.message}")

            else:
                print(f"{get_current_time()} Error: Wrong choice. Try again!")


if __name__ == "__main__":
    unique_id = str(uuid.uuid1())
    port = 50052
    run(port, unique_id)