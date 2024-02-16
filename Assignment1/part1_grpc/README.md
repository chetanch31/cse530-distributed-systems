# Project README

This project implements a simple gRPC-based market service, allowing sellers to register, sell items, update item details, delete items, and display their listed items. Buyers can search for items, buy items, add items to their wishlist, and rate items.

## How to Run

### Prerequisites

- Python 3.x installed on your system
- gRPC Python library (`grpcio`) installed. You can install it using pip:
  
  ```bash
  pip install -r requirements.txt
  ```

### Files

market.py : Main server for market
seller.py : Connects to market. Hosts a notificaiton server
buyer.py  : Conencts to market to interact with sellers. Hosts a notification server