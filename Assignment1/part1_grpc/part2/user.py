import zmq
from datetime import datetime

#Constants
MSG_APP_IP = "localhost"
MSG_APP_PORT = 5556
GROUP_IP = "127.0.0.1"
GROUP_PORT=5557

#things / cases pending to add in this file
#users to have unique id's
#users to store which groups they are currently a part of, and they can send messages to only those groups.

class User:
    
    # ID_COUNT=0
    
    def __init__(self,user_name):
        self.groups = []
        self.user_name = user_name
        self.uuid = self.generate_uuid()
        
    def generate_uuid(self):
        # Generate a numerical user UUID starting from 1
        return str(len(self.groups) + 1)
            
    def join_group(self, group_port, user_name):
        
        context = zmq.Context()
        group_socket=context.socket(zmq.REQ)
        group_socket.setsockopt(zmq.LINGER, 0)
        # Send join request to the group server
        request = f"JOIN_GROUP {group_port} {self.uuid} {user_name}"
        group_socket.connect("tcp://{}:{}".format(GROUP_IP, group_port))
        #external IP address of the group server

        group_socket.send_string(request)
        
        print("Joining group on port ", group_port)

        response = group_socket.recv_string()

        print("Response from group server:", response)
        
        if response.startswith("SUCCESS"):
            self.groups.append(group_port)
            print(group_port, " joined successfully")
        else:
            print("Failed to join the group.")

    def leave_group(self, group_port,user_name):
        
        context = zmq.Context()
        group_socket=context.socket(zmq.REQ)
        group_socket.setsockopt(zmq.LINGER, 0)
        # Send leave request to the group server
        request = f"LEAVE_GROUP {group_port} {self.uuid} {user_name}"
        group_socket.connect("tcp://{}:{}".format(GROUP_IP, group_port))

        group_socket.send_string(request)
        
        response = group_socket.recv_string()
        print("Response from group server:", response)
        
        if response.startswith("SUCCESS"):
            self.groups.remove(group_port)
            print(group_port, "left succesfully")
        else:
            print("Failed to leave the group.")

    def send_message(self, group_port, message_content):
        
        context = zmq.Context()
        group_socket=context.socket(zmq.REQ)
        group_socket.setsockopt(zmq.LINGER, 0)
        # Send join request to the group server

        group_socket.connect("tcp://{}:{}".format(GROUP_IP, group_port))
        
        # Send message to the message server
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        request = f"SEND_MESSAGE {group_port} {timestamp} {self.uuid} {message_content}"
        group_socket.send_string(request)
        response = group_socket.recv_string()
        print("\nResponse from group server:", response)

    def view_messages(self, group_port, timestamp=None):
        
        context = zmq.Context()
        group_socket=context.socket(zmq.REQ)
        group_socket.setsockopt(zmq.LINGER, 0)
        # Send join request to the group server

        group_socket.connect("tcp://{}:{}".format(GROUP_IP, group_port))
        
        # Send request to view messages from the message server
        if timestamp:
            request = f"GET_MESSAGES {group_port} {timestamp}"
        else:
            request = f"GET_MESSAGES {group_port}"
            
        group_socket.send_string(request)
        response = group_socket.recv_string()
        print("Messages in group '{}':\n{}".format(group_port, response))

    def request_group_list(self, socket):
        # Request the list of existing groups from the message server
        socket.send_string("GET_GROUP_LIST")
        response = socket.recv_string()
        print("List of existing groups:", response)

def main():
    
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://{}:{}".format(MSG_APP_IP, MSG_APP_PORT))
    
    user_name = input("Enter your username: ")
    user = User(user_name)

    print(f"\nWelcome to the Message App!\n")
    
    # Implement user interactions
    while True:

        print("\nMenu:")
        print("1. Join group")
        print("2. Leave group")
        print("3. Send message")
        print("4. View messages")
        print("5. View group list")
        print("6. Exit\n")

        choice = input("Enter your choice: ")

        if choice == "1":
            group_port = input("Enter the group port to join: ")
            if group_port in user.groups:
                print("You are already a part of this group.")
            else:
                user.join_group(group_port, user_name)
        elif choice == "2":
            group_port = input("Enter the group port to leave: ")
            if group_port not in user.groups:
                print("You are not a part of this group.")
            else:
                user.leave_group(group_port,user_name)
        elif choice == "3":
            group_port = input("Enter the group port to send message: ")
            message_content = input("Enter your message: ")
            if group_port in user.groups:
                user.send_message(group_port, message_content)
            else:
                print("You are not a part of this group. Please join the group first.")
        elif choice == "4":
            group_port = input("Enter the group port to view messages: ")
            timestamp = input("Enter timestamp (YYYY-MM-DD HH:MM:SS) or press Enter for all messages: ")
            if group_port in user.groups:
                user.view_messages(group_port, timestamp)
            else:
                print("You are not a part of this group. Please join the group first.") 
                
        elif choice == "5":
            user.request_group_list(socket)

        elif choice == "6":
            print("Exiting the Message App")
            socket.close()
            # groupSocketMain.close()
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
