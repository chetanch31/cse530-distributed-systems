import pika

input1 = input("Enter Command")
parts = input1.split()
name = parts[0]

def updatesubscription():
    # Establish connection to RabbitMQ server
    credentials = pika.PlainCredentials("username","password")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='34.133.227.248', credentials=credentials))
    channel = connection.channel()

    # Declare a direct exchange
    channel.exchange_declare(exchange='User_exchange_server', exchange_type='direct')

    # Send a message with a routing key    
    message = input1
    channel.basic_publish(exchange='User_exchange_server', routing_key='user_key', body=message)
    print("SUCCESS", message)

    # Close the connection
    connection.close()


def receiveNotifications():
#RECEIVING NOTIFICATIONS BELOW
    
    # Establish connection to RabbitMQ server
    credentials = pika.PlainCredentials("username","password")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='34.133.227.248', credentials=credentials))
    channel = connection.channel()

    # Declare a direct exchange
    channel.exchange_declare(exchange='Video_Notifications', exchange_type='direct')

    # Declare a queue
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind the queue to the exchange with a specific routing key
    channel.queue_bind(exchange='Video_Notifications', queue=queue_name, routing_key=name)

    # Set up a consumer and start consuming messages
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print('Waiting for messages...')
    channel.start_consuming()


# Callback function to handle incoming messages
def callback(ch, method, properties, body):
    print("Received:", body)

if __name__ == "__main__":
    updatesubscription()
    receiveNotifications()
