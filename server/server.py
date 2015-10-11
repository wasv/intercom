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

    def heartbeat(self):
        if not self.alive:
            self.transport.loseConnection()
            print("Lost client")
            self.factory.clients.remove(self)
        else:
          self.alive = False
          reactor.callLater(15.0, self.heartbeat)

    def __init__(self, isock):
        self.isock = isock
        reactor.callLater(1.0, self.readFromIn)
        reactor.callLater(15.0, self.heartbeat)

    def lineReceived(self, line):
        """
        As soon as any data is received, write it back.
        """
        line = line.decode('utf-8','ignore')
        if line is "<3<3":
            self.alive = True

    def connectionMade(self):
        print("Got Client")
        self.factory.clients.append(self)

    def connectLost(self, reason):
        print("Lost client")
        self.factory.clients.remove(self)

    def readFromIn(self):
        for ins in select.select([self.isock, sys.stdin] + self.inputs, [], [], 1)[0]:
            line = self.readline(ins)
            if line:
                parts = line.split('|')
                parts[0] =str(time.time()+float(parts[0]))
                line = '|'.join(parts)
                print(line)
                for c in self.factory.clients:
                    print(c)
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
    clients = []

    def __init__(self, istream):
        self.istream = istream

    def buildProtocol(self, addr):
        p = self.protocol(self.istream)
        p.factory = self
        return p

    def stopFactory(self):
        if self.istream: self.istream.close()

def main():
    host = socket.gethostbyname("localhost")
    port = 42420
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host,port))
    s.listen(4)
    f=EchoFactory(s)
    f.clients=[]
    reactor.listenTCP(42421,f)
    reactor.run()

if __name__ == '__main__':
    main()
