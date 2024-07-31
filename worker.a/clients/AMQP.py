import os
import pika


class Client:
    q1_name = os.getenv('QUEUE_1_NAME', 'queue_1')
    q2_name = os.getenv('QUEUE_2_NAME', 'queue_2')
    def __init__(self, queue_name):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.ch1 = self.connection.channel()
        self.ch1.queue_declare(queue=self.q1_name, durable=True, exclusive=False, auto_delete=False)
        self.ch2 = self.connection.channel()
        self.ch2.queue_declare(queue=self.q2_name, durable=True, exclusive=False, auto_delete=False)
        self.consumer_tag = 'worker_1'

    def consume(self, callback, auto_ack=False, max_messages=1):
        self.ch1.basic_qos(prefetch_count=max_messages, global_qos=False)
        self.ch1.basic_consume(queue=self.q1_name, on_message_callback=callback, auto_ack=auto_ack, consumer_tag=self.consumer_tag)
        self.ch1.start_consuming()

    def publish(self, message):
        pass

    def close(self):
        self.connection.close()
