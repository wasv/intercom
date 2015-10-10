#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import time
import select
import sys
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, protocol, endpoints, task
### Protocol Implementation

# This is just about the simplest possible protocol
class Echo(LineReceiver):
    def __init__(self):
        reactor.callLater(1.0, self.readFromIn)

    def lineReceived(self, line):
        """
        As soon as any data is received, write it back.
        """
        print(line.decode('utf-8','ignore'))

    def connectionMade(self):
        print("Got Client")
        self.factory.clients.append(self)

    def connectLost(self, reason):
        print("Lost client")
        self.factory.cleints.remove(self)

    def readFromIn(self):
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline().strip()
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
