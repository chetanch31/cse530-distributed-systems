import zmq

# Constants
MSG_APP_PORT = 5556

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("10.128.0.2" + str(MSG_APP_PORT))

    groups = {}  # Dictionary to store group names and IP addresses
    
    while True:
        message = socket.recv_string()
        print("Message App Server received:", message)
        
        # Parse message to identify request type
        request_parts = message.split(" ")
        request_type = request_parts[0]
        
        if request_type == "REGISTER_GROUP":
            # Example: REGISTER_GROUP group_name IP_address
            group_name = request_parts[1]
            ip_address = request_parts[2]
            groups[group_name] = ip_address
            print("Group '{}' registered with IP address '{}'".format(group_name, ip_address))
            socket.send_string("SUCCESS")
        
        elif request_type == "GET_GROUP_LIST":
            # Send list of group names and their IP addresses to group.py
            response = "\n".join(["{} - {}".format(group, ip) for group, ip in groups.items()])
            socket.send_string(response)
            print("Sent group list to User Server:", response)
        
        else:
            # Invalid request type
            socket.send_string("INVALID_REQUEST")

if __name__ == "__main__":
    main()
