#!/usr/bin/env python

from __future__ import print_function
import hashlib

try:
    input = raw_input
except NameError:
    pass

class Sender:
    publicid = 'test'
    privateid = 'qwerty123'.encode('utf-8','ignore')

    def make_message(self, message):
        bmessage = message.encode('utf-8','ignore')
        checksum = hashlib.md5(bmessage+self.privateid).hexdigest()
        return self.publicid+'%'+message+'%'+checksum

    def __init__(self,publicid=None,privateid=None):
        if publicid:
            self.publicid = publicid
        if privateid:
            self.privateid = privateid.encode('utf-8','ignore')

def main():
    import socket
    host = "localhost"
    port = 42420
    try:
        host = open("server.txt").read()
    except Exception as e:
        print(e)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    print("Connected")
    sender = Sender()
    message = input("Enter message ")
    auth_message = sender.make_message(message)
    s.send(auth_message.encode('utf-8','ignore'))
    print(auth_message)

if __name__ == '__main__':
    main()
