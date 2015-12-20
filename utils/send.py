#!/usr/bin/env python

from __future__ import print_function
import hashlib

try:
    input = raw_input
except NameError:
    pass

class Sender:
    def make_message(self, message):
        bmessage = message.encode('utf-8','ignore')
        checksum = hashlib.md5(bmessage+self.privateid).hexdigest()
        return self.publicid+'%'+message+'%'+checksum

    def __init__(self,publicid, privateid):
        if publicid:
            self.publicid = publicid
        if privateid:
            self.privateid = privateid.encode('utf-8','ignore')

def main():
    import socket, time
    host = "localhost"
    port = 42420

    try:
        host = open("server.key.txt").read().strip()
    except Exception as e:
        print("WARN: ",e)
    print("Connected to",host)

    authpair = ['test','qwerty123']
    try:
        authpair = open("myauth.key.txt").read().strip().split(' ')
    except Exception as e:
        print("WARN: ",e)

    sender = Sender( authpair[0], authpair[1] )
    while True:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((host,port))
      message = input("Enter message: ")
      auth_message = sender.make_message(message)
      s.send(auth_message.encode('utf-8','ignore'))
      s.close()
      time.sleep(3)
      print(auth_message)

if __name__ == '__main__':
    main()
