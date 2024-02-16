from concurrent import futures
from datetime import datetime

import grpc
import task_pb2
import task_pb2_grpc

class Market(task_pb2_grpc.MarketServicer):

    seller_list = {}
    item_list = {}
    wish_list = {}

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
            "rating" : 0,
            "rated_by" : []
        }

        # print(self.item_list)
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
            # print("Before:", self.item_list[item_id])

            self.item_list[item_id]["price"] = request.new_price
            self.item_list[item_id]["quantity"] = request.new_quantity
        
            # print("After:", self.item_list[item_id])

            response = task_pb2.UpdateItemResponse(
                status = task_pb2.UpdateItemResponse.SUCCESS,
                message = "Item updated successfully!"
            )

            updated_item = self.item_list[item_id]
            send_item = task_pb2.SellerItem(
                item_id=item_id,
                price=updated_item["price"],
                product_name=updated_item["name"],
                category=str(updated_item["category"]),
                description=updated_item["description"],
                quantity_remaining=updated_item["quantity"],
                seller_address=self.seller_list.get(request.seller_uuid, "Unknown"),
                rating=updated_item["rating"]
            )
            message = f"\n{self.get_current_time()} Item in your wishlist has been updated. {item_id}"
            # print(self.wish_list[item_id])
            
            for buyer_addr in self.wish_list[item_id]:
                with grpc.insecure_channel(buyer_addr) as channel:
                    stub = task_pb2_grpc.MarketStub(channel)
                    request = task_pb2.NotificationRequest(
                        message = message,
                        item = send_item
                    )
                    reply = stub.SendNotification(request)
                    print(reply)

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
            print(f"{self.get_current_time()} Deleting item {item_id}")
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
            print(f"{self.get_current_time()} Seller not registered")

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

        
        # print("Printing seller items", seller_items)
        response = task_pb2.DisplaySellerItemsResponse(
            status=task_pb2.DisplaySellerItemsResponse.Status.SUCCESS,
            message="Completed successfully!",
            items=seller_items
        )
        
        return response

    def SearchItem(self, request, context):
        name, category = request.name, request.category
        print(f"{self.get_current_time()} Search request for item name: {name}, category: {category}")

        matched_items = []

        for item_id, item in self.item_list.items():
            if (not name or name.lower() in item["name"].lower()) and \
            (not category or str(category) == "ANY" or category == item["category"]):
                seller_address = self.seller_list.get(item["uid"], "Unknown")
                seller_item = task_pb2.SellerItem(
                    item_id=item_id,
                    price=item["price"],
                    product_name=item["name"],
                    category=str(item["category"]),
                    description=item["description"],
                    quantity_remaining=item["quantity"],
                    seller_address=seller_address,
                    rating=item["rating"]
                )
                matched_items.append(seller_item)
        
        # print("Matched item list")
        # print(matched_items)

        if len(matched_items) != 0:
            response = task_pb2.BuyerSearchItemResponse(
                status=task_pb2.BuyerSearchItemResponse.Status.SUCCESS,
                message="Search completed successfully!",
                items=matched_items
            )
            return response
        
        response = task_pb2.BuyerSearchItemResponse(
            status=task_pb2.BuyerSearchItemResponse.Status.FAILED,
            message="No results found",
            items=matched_items
        )
        return response

    def BuyItem(self, request, context):
        item_id = request.item_id
        quantity = request.quantity
        buyer_address = request.buyer_address

        print(f"{self.get_current_time()} Buy request of quantity {quantity} for item ID {item_id} from {buyer_address}")
        # Check if the item exists
        if item_id not in self.item_list:
            response = task_pb2.BuyItemResponse(
                status=task_pb2.BuyItemResponse.Status.FAILED,
                message=f"Item with ID {item_id} not found"
            )
            return response

        # Check if there is enough quantity available
        if self.item_list[item_id]["quantity"] < quantity:
            response = task_pb2.BuyItemResponse(
                status=task_pb2.BuyItemResponse.Status.FAILED,
                message=f"Not enough quantity available for item with ID {item_id}"
            )
            return response

        # Update item quantity after purchase
        self.item_list[item_id]["quantity"] -= quantity

        # Trigger notification to the seller
        seller_uuid = self.item_list[item_id]["uid"]
        seller_address = self.seller_list.get(seller_uuid, "Unknown")
        seller_notification = f"Buy request {quantity} of item {item_id}, from {buyer_address}"
        print(f"{self.get_current_time()} Seller notification: {seller_notification}")

        # Prepare the response

        with grpc.insecure_channel(seller_address) as channel:
            stub = task_pb2_grpc.MarketStub(channel)
            item = self.item_list[item_id]
            send_item = task_pb2.SellerItem(
                    item_id=item_id,
                    price=item["price"],
                    product_name=item["name"],
                    category=str(item["category"]),
                    description=item["description"],
                    quantity_remaining=item["quantity"],
                    seller_address=seller_address,
                    rating=item["rating"]
                )
            message = f"{self.get_current_time()} Item sold to buyer {buyer_address}"

            req = task_pb2.NotificationRequest(
                message = message,
                item = send_item
            )
            
            reply = stub.SendNotification(req)
            print(reply)

        response = task_pb2.BuyItemResponse(
            status=task_pb2.BuyItemResponse.Status.SUCCESS,
            message="Item purchased successfully!"
        )
        return response

    def AddToWishList(self, request, context):
        item_id = request.item_id
        buyer_address = request.buyer_address

        print(f"{self.get_current_time()} Wishlist request of item {item_id} from {buyer_address}")
        # Check if the item ID exists in the item list
        if item_id not in self.item_list:
            response = task_pb2.AddToWishListResponse(
                status=task_pb2.AddToWishListResponse.Status.FAILED,
                message=f"Item with ID {item_id} does not exist"
            )
            return response
        
        if self.wish_list.get(item_id) and buyer_address in self.wish_list[item_id]:
            response = task_pb2.AddToWishListResponse(
                status=task_pb2.AddToWishListResponse.Status.FAILED,
                message=f"Item with ID {item_id} is already in the wishlist for buyer at {buyer_address}"
            )
            return response
        # Add the buyer's address to the wishlist for the item
        if item_id in self.wish_list:
            self.wish_list[item_id].append(buyer_address)
        else:
            self.wish_list[item_id] = [buyer_address]

        # Send a success response
        response = task_pb2.AddToWishListResponse(
            status=task_pb2.AddToWishListResponse.Status.SUCCESS,
            message=f"Item with ID {item_id} added to wishlist for buyer at {buyer_address}"
        )

        # print(self.wish_list)
        return response
    
    def RateItem(self, request, context):
        item_id = request.item_id
        buyer_address = request.buyer_address
        rating = request.rating

        print(f"{self.get_current_time()} {buyer_address} rated item {item_id} with {rating} stars.")

        # Check if the item ID exists in the item list
        if item_id not in self.item_list:
            response = task_pb2.RateItemResponse(
                status=task_pb2.RateItemResponse.Status.FAILED,
                message=f"Item with ID {item_id} does not exist"
            )
            return response

        # Check if the rating is valid (between 1 and 5)
        if rating < 1 or rating > 5:
            response = task_pb2.RateItemResponse(
                status=task_pb2.RateItemResponse.Status.FAILED,
                message="Rating must be between 1 and 5"
            )
            return response

        # Check if the buyer has already rated this item
        if buyer_address in self.item_list[item_id]["rated_by"]:
            response = task_pb2.RateItemResponse(
                status=task_pb2.RateItemResponse.Status.FAILED,
                message="You have already rated this item"
            )
            return response

        # Update the item's rating and add the buyer's address to the list of rated_by
        current_rating = self.item_list[item_id]["rating"]
        current_count = len(self.item_list[item_id]["rated_by"])
        new_rating = ((current_rating * current_count) + rating) / (current_count + 1)
        self.item_list[item_id]["rating"] = new_rating

        self.item_list[item_id]["rated_by"].append(buyer_address)

        # Send a success response
        response = task_pb2.RateItemResponse(
            status=task_pb2.RateItemResponse.Status.SUCCESS,
            message="Item rated successfully!"
        )

        # print(self.item_list[item_id])
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
