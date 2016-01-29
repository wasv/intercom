from __future__ import print_function
import send
import socket, time, random

# Create default sender method
sender = send.Sender('test', 'qwerty123')

while True:
    message = random.choice(["Hello New York", "Hello", "42"])
    auth_message = sender.make_message(message)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 42420))
    s.send(auth_message.encode('utf-8', 'ignore'))
    s.close()
    print(str(time.time()), auth_message)
    time.sleep(15)
