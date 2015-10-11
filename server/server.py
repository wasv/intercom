#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import time
import select
import sys
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, protocol, endpoints, task
### Protocol Implementation

class Echo(LineReceiver):
    alive = True
    istream = sys.stdin

    def heartbeat(self):
        if not self.alive:
            self.transport.loseConnection()
            print("Lost client")
            self.factory.clients.remove(self)
        else:
          self.alive = False
          reactor.callLater(15.0, self.heartbeat)

    def __init__(self):
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
        if self.istream in select.select([self.istream], [], [], 0)[0]:
            line = self.istream.readline().strip()
            if line:
                parts = line.split('|')
                parts[0] =str(time.time()+float(parts[0]))
                line = '|'.join(parts)
                print(line)
                for c in self.factory.clients:
                    print(c)
                    c.message(line.encode('utf-8'))
            else: # an empty line means stdin has been closed
                print('eof')
        reactor.callLater(1.0, self.readFromIn)

    def message(self, message):
        self.sendLine(message)

def main():
    f = protocol.Factory()
    f.protocol = Echo
    f.clients = []
    reactor.listenTCP(8000, f)
    reactor.run()

if __name__ == '__main__':
    main()
