#!/bin/bash

# Define the port numbers for the buyers
port1="$1"
port2="$2"

# Launch the first buyer in a new terminal with port1
gnome-terminal -- python buyer.py --port "$port1"

# Launch the second buyer in a new terminal with port2
gnome-terminal -- python buyer.py --port "$port2"
