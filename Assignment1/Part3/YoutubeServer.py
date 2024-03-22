import pika
import threading

#Dictionary to store subscribers of YouTubers
youtuber_subscribers = {
    "PewDiePie": ["Alice", "Bob", "Charlie"],
    "MrBeast": ["David", "Emma", "Frank"],
    "Markiplier": ["Grace", "Henry", "Isabella"] #random data dumping
}

# Function to add a subscriber to a YouTuber
def add_subscriber(youtuber_name, subscriber_name):
    if youtuber_name in youtuber_subscribers:
        youtuber_subscribers[youtuber_name].append(subscriber_name)
    else:
        youtuber_subscribers[youtuber_name] = [subscriber_name]
    print(subscriber_name + " subscribed to " + youtuber_name)

# Function to remove a subscriber from a YouTuber
def remove_subscriber(youtuber_name, subscriber_name):
    if youtuber_name in youtuber_subscribers and subscriber_name in youtuber_subscribers[youtuber_name]:
        youtuber_subscribers[youtuber_name].remove(subscriber_name)
        print(f"{subscriber_name} has been removed from {youtuber_name}'s subscribers.")
    else:
        print(f"{subscriber_name} is not subscribed to {youtuber_name}.")

# Function to handle incoming messages for YouTuber
def youtuber_callback(ch, method, properties, body):
    yt, video = body.decode('utf-8').split(maxsplit=1)  # Splitting into two parts
    print(yt +" uploaded " + video)
    send_notifications(yt,video)

def user_callback(ch, method, properties, body):
    message = body.decode('utf-8')
    parts = message.split()
    
    if len(parts) == 1:
        # If it's just a name
        print(f"{parts[0]} logged in")
    elif len(parts) == 3:
        # If it's a subscribe or unsubscribe command
        name = parts[0]
        action = parts[1]
        youtuber = parts[2]
        if action == 's':
            add_subscriber(youtuber,name)
        elif action == 'u':
            print(f"{name} unsubscribed from {youtuber}")
            remove_subscriber(youtuber,name)
        else:
            print("Invalid action")
    else:
        print("Invalid message format")


# Function to establish connection and start consuming messages for YouTuber
def youtuber_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='Youtuber_exchange_server', exchange_type='direct')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='Youtuber_exchange_server', queue=queue_name, routing_key='video_user')

    channel.basic_consume(queue=queue_name, on_message_callback=youtuber_callback, auto_ack=True)

    print('Waiting for YouTuber messages...')
    channel.start_consuming()

# Function to establish connection and start consuming messages for User
def user_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='User_exchange_server', exchange_type='direct')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='User_exchange_server', queue=queue_name, routing_key='user_key')

    channel.basic_consume(queue=queue_name, on_message_callback=user_callback, auto_ack=True)

    print('Waiting for User messages...')
    channel.start_consuming()

def send_notifications(youtuber, video):
    # Establish connection to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare a direct exchange
    channel.exchange_declare(exchange='Video_Notifications', exchange_type='direct')

    # Iterate through the subscribers of the YouTuber
    for subscriber_name in youtuber_subscribers.get(youtuber, []):
        # Send a message with a routing key
        message = f"{youtuber} published {video}"
        channel.basic_publish(exchange='Video_Notifications', routing_key=subscriber_name, body=message)
        print(f"Notification sent to {subscriber_name}: {message}")

    # Close the connection
    connection.close()


# Create threads for each consumer
youtuber_thread = threading.Thread(target=youtuber_consumer)
user_thread = threading.Thread(target=user_consumer)

# Start both threads
youtuber_thread.start()
user_thread.start()

