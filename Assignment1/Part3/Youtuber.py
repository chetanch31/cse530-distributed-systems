import pika

def publish_video():
    # Establish connection to RabbitMQ server
    credentials = pika.PlainCredentials("username","password")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='34.133.227.248', credentials=credentials))
    channel = connection.channel()

    # Declare a direct exchange
    channel.exchange_declare(exchange='Youtuber_exchange_server', exchange_type='direct')

    message = input("Enter YoutuberName Video")
    channel.basic_publish(exchange='Youtuber_exchange_server', routing_key="video_user", body=message)
    print("Message sent:", message)

    # Close the connection
    connection.close()


if __name__ == "__main__":
    publish_video()