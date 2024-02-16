import zmq
import socket

# Constants
MSG_APP_IP = "localhost"
MSG_APP_PORT = 5556
GROUP_IP = "localhost"
# GROUP_PORT = 5557

class Group:
        
    def __init__(self, name, port=None):
        self.name = name
        self.port = port
        print("Assigned port:", self.port)  # Debugging print
        self.users = {}  # Dictionary to store users with their UUIDs as keys
        self.messages = []  # List to store messages with their timestamps
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.port}")
        #internalIP address of the group server
        self.socket.setsockopt(zmq.RCVTIMEO, 1000000)  # Set timeout for receive operation
        
    # @classmethod
    # def assign_port(cls):
    #     cls.last_assigned_port += 1
    #     print("Last assigned port:", cls.last_assigned_port)
    #     return cls.last_assigned_port

    def add_user(self, user_uuid):
        self.users[user_uuid] = True  # You can use a boolean value to represent user membership

    def remove_user(self, user_uuid):
        if user_uuid in self.users:
            del self.users[user_uuid]  # Remove the user from the dictionary if present

    def add_message(self, message_content, timestamp):
        self.messages.append((message_content, timestamp))  # Store the message along with its timestamp

    def get_messages(self, timestamp=None):
        if timestamp:
            # If timestamp is provided, filter messages after the given timestamp
            filtered_messages = [msg for msg in self.messages if msg[1] >= timestamp]
        else:
            # If timestamp is not provided, return all messages
            filtered_messages = self.messages

        # Format the messages for response
        response = "\n".join([f"{msg[1]}: {msg[0]}" for msg in filtered_messages])
        return response

    def register_group(self, message_server_ip, message_server_port):
        
        # Connect to the message server
        main_server_context = zmq.Context()
        main_server_socket = main_server_context.socket(zmq.REQ)
        main_server_socket.connect("tcp://{}:{}".format(message_server_ip, message_server_port))

        try:
            # Send a request to the message server to register the group
            request = f"REGISTER_GROUP {self.name} {GROUP_IP}:{self.port}"
            main_server_socket.send_string(request)
            
            # Receive response from the message server
            response = main_server_socket.recv_string()
            print("Server prints:", response)
            
            if response == "SUCCESS":
                print("Group server registered successfully.")
            else:
                print("Failed to register group server.")
        except Exception as e:
            print("Error while registering group server:", str(e))

    def handle_join_request(self,message):
        
        try:
            # Split the received message to get group port, user UUID, and user name
            parts = message.split(maxsplit=2)
            if len(parts) == 3:
                group_port, user_uuid, user_name = parts
                # Add user to the group
                self.add_user(user_uuid)
                # Send response back to the user
                self.socket.send_string(f"SUCCESS: User {user_name} joined the group on port {group_port}")
            else:
                raise ValueError("Invalid message format")
        except Exception as e:
            print("Error in joining the group:", str(e))
            self.socket.send_string("FAIL: Error in joining the group")

    def handle_leave_request(self,message):
        try:
            parts = message.split(maxsplit=2)
            print("Received leave request:", message)

            if len(parts) == 3:
                group_port, user_uuid, username = parts
                self.remove_user(user_uuid)        
                self.socket.send_string(f"SUCCESS: User {username} left the group on port {group_port}")
            else:
                raise ValueError("Invalid message format")
        except Exception as e:
            print("Error in leaving the group:", str(e))
            self.socket.send_string("FAIL: Error in leaving the group")

    def handle_message_request(self,message):
        try:
            parts = message.split(maxsplit=3)
            if len(parts) == 4:
                group_port, timestamp, uuid, message_content = parts
                # Add message to the group
                self.add_message(message_content, timestamp)
                # Send response back to the user
                self.socket.send_string("SUCCESS: Message stored successfully")
            else:
                raise ValueError("Invalid message format")
                        
        except Exception as e:
            print("Error in storing message:", str(e))
            self.socket.send_string("FAIL: Error in storing message")

    def handle_get_messages_request(self,message):
        try:
            
            # Split the received message to get group name and timestamp
            parts= message.split(maxsplit=1)
            if len(parts) == 2:
                group_name, timestamp = parts
                # Get messages from the group
                messages = self.get_messages(timestamp)
                # Send response back to the user
                self.socket.send_string(messages)
            elif len(parts) == 1:
                group_name = parts
                messages = self.get_messages()
                self.socket.send_string(messages)
            else:
                raise ValueError("Invalid message format")
            
        except Exception as e:
            print("Error in retrieving messages:", str(e))
            self.socket.send_string("FAIL: Error in retrieving messages")

    def is_port_in_use(port):
        # Create a new socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set a short timeout to speed up the check
        s.settimeout(1)
    
        try:
            # Attempt to bind the socket to the specified port
            s.bind(('localhost', int(port)))
        except OSError as e:
            # If binding fails with "Address already in use" error,
            # it means the port is already in use
            if e.errno == socket.errno.EADDRINUSE:
                return True
            else:
                # If it fails for some other reason, it's likely an unexpected error
                print("Unexpected error:", e)
        finally:
            # Close the socket
            s.close()
        
        # If the binding was successful, the port is not in use
        return False

def main():
    
    # Create a group server instance
    group_name = input("Enter group name: ")
    # group_port = GROUP_PORT  # Assuming the group server always listens on the same port
    
    group_port = input("Enter group port: ")
    #if group_port in use then ask user to enter another port
    while Group.is_port_in_use(group_port):
        print("Port is already in use, please enter another port")
        group_port = input("Enter group port: ")        
   
    group = Group(group_name, group_port)
    
    group.register_group(MSG_APP_IP,MSG_APP_PORT)
    
    # Start handling requests
    print(f"Group '{group_name}' is now active on port {group.port}.")
    while True:
        try:
            # Receive a message
            message = group.socket.recv_string()
            print("Received message:", message)
            
            # Handle the received message based on its content
            if message.startswith("JOIN"):
                group.handle_join_request(message)
            elif message.startswith("LEAVE"):
                group.handle_leave_request(message)
            elif message.startswith("SEND_MESSAGE"):
                group.handle_message_request(message)
            elif message.startswith("GET_MESSAGES"):
                group.handle_get_messages_request(message)
            else:
                print("Unknown message type:", message)
        except KeyboardInterrupt:
            print("Exiting...")
            group.socket.close()
            break

if __name__ == "__main__":
    main()
