#!/usr/bin/env python

from __future__ import print_function
import hashlib

# Tiny shim to ensure backwards compatibility.
try:
    input = raw_input
except NameError:
    pass

# Class to create sender object with specified IDs.
class Sender:
    def make_message(self, message):
        """
            Adds checksum and metadata to message.
            :param message: message to encode
            :return: encoded message
        """
        bmessage = message.encode('utf-8', 'ignore')
        checksum = hashlib.md5(bmessage + self.privateid).hexdigest()
        return self.publicid + '%' + message + '%' + checksum

    def __init__(self, publicid, privateid):
        """
            Initialize the sender with a public and private id.
            :param publicid: public identifier, sent with message.
            :param privateid: private identifier, shared secret between devices.
            :return:
        """
        if publicid:
            self.publicid = publicid
        if privateid:
            self.privateid = privateid.encode('utf-8', 'ignore')


def main():
    """
        Start main loop for sending messages.
        :return: Nothing
    """
    import socket, time
    host = "localhost"
    port = 42420

    # Read server from config file.
    try:
        host = open("server.key.txt").read().strip()
    except Exception as e:
        print("WARN: ", e)
    print("Connected to", host)

    # Default authpair.
    authpair = ['test', 'qwerty123']

    # Read my authpair from config file.
    try:
        authpair = open("myauth.key.txt").read().strip().split(' ')
    except Exception as e:
        print("WARN: ", e)

    # Create sender object with my authpair.
    sender = Sender(authpair[0], authpair[1])
    while True:
        # Open socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        # Read, encode, and send message.
        message = input("Enter message: ")
        auth_message = sender.make_message(message)
        s.send(auth_message.encode('utf-8', 'ignore'))

        # Close socket.
        s.close()
        time.sleep(3) # Slight delay to ensure socket closes.
        print(auth_message)


if __name__ == '__main__':
    main()
