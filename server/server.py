#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import time
import select
import sys
import socket
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, protocol, endpoints, task
### Protocol Implementation

class Echo(LineReceiver):
    alive = True
    inputs = []

    def __init__(self, isock):
        self.isock = isock
        reactor.callLater(1.0, self.readFromIn)

    def lineReceived(self, line):
        """
        As soon as any data is received, write it back.
        """
        line = line.decode('utf-8','ignore')
        if line is "<3<3":
            self.alive = True

    def readFromIn(self):
        for ins in select.select([self.isock, sys.stdin] + self.inputs, [], [], 1)[0]:
            line = self.readline(ins)
            if line:
                parts = line.split('|')
                parts[0] =str(time.time()+float(parts[0]))
                line = '|'.join(parts)
                print(line)
                for h in self.factory.clients:
                    print("Sent message to",h)
                    c = self.factory.clients[h]
                    c.message(line.encode('utf-8'))
        reactor.callLater(1.0, self.readFromIn)

    def readline(self,ins):
        if ins == self.isock:
            client, _ = ins.accept()
            self.inputs.append(client)
            return None
        elif ins == sys.stdin:
            return sys.stdin.readline().strip()
        else:
            data = ins.recv(1024)
            print(data)
            ins.close()
            self.inputs.remove(ins)
            if data:
                return data.decode('utf-8','ignore')
            else:
                return None

    def message(self, message):
        self.sendLine(message)

class EchoFactory(protocol.Factory):
    protocol = Echo
    clients = {}

    def __init__(self, istream):
        self.istream = istream

    def buildProtocol(self, addr):
        addr = addr.host 
        if addr not in self.clients:
          print("New client",addr)
          self.clients[addr] = self.protocol(self.istream)
          self.clients[addr].factory = self
        else:
          print("Reconnection from",addr)
        p = self.clients[addr]
        return p

    def stopFactory(self):
        if self.istream: self.istream.close()

def main():
    host = ""
    port = 42420
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host,port))
    s.listen(4)
    f=EchoFactory(s)
    reactor.listenTCP(42124,f)
    reactor.run()

if __name__ == '__main__':
    main()
