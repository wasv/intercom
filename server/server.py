#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from __future__ import print_function
import time
import select
import os
import sys
import socket
import hashlib
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, protocol, endpoints, task


### Protocol Implementation

class Relay(LineReceiver):
    # Array to hold currently connected telnet input streams.
    inputs = []

    def authenticate(self, data):
        """
            Authenticates data using an md5 hash.
            Expects a string of format publicid % message % md5(message+privateid)
        """

        data = data.strip().split('%')
        if len(data) != 3:
            raise Exception("Invalid Message")
        try:
            privateid = self.factory.authkeys[data[0]].encode('utf-8', 'ignore')
        except:
            raise Exception("Invalid Authkey")
        message = data[1].encode('utf-8', 'ignore')
        checksum = hashlib.md5(message + privateid).hexdigest()
        if data[2] == checksum:
            return message.decode('utf-8', 'ignore')
        else:
            raise Exception("Failed auth")

    def __init__(self, istreams):
        """
            Initializes the Relay protocol handler with the specified input streams.
        """
        self.istreams = istreams
        self.istreams.append(sys.stdin)
        reactor.callLater(1.0, self.readFromIn)

    def readFromIn(self):
        """
            Check for input from input streams.
            :return: Nothing.
        """
        for ins in select.select(self.istreams + self.inputs, [], [], 1)[0]:
            try:
                line = self.readline(ins)
            except Exception as e:
                print(e)
                continue
            if line != None and line != "":
                parts = line.split('|')
                parts[0] = parts[0].strip()
                if len(parts) > 1:
                    try:
                        parts[-1] = str(time.time() + float(parts[-1]))
                    # If any of the above fails, then last part is not a float. Use default value.
                    except ValueError:
                        parts.append(str(time.time() + 1))
                else:
                    parts.append(str(time.time() + 1))

                # Once message is parsed, reassemble it and send it to clients.
                line = ' '.join(parts[:-1])
                line = line + '|' + parts[-1]
                print(line)
                for h in self.factory.clients:
                    print("Sent message to", h)
                    c = self.factory.clients[h]
                    c.message(line.encode('utf-8'))
        # Repeat every second.
        reactor.callLater(1.0, self.readFromIn)

    def readline(self, ins):
        """
            A helper function to determine which input stream is given and reads from it.
        """
        if isinstance(ins, socket.socket):  # Is it a socket?
            if ins in self.inputs:  # Is it a current client?
                data = ins.recv(255)
                ins.close()
                self.inputs.remove(ins)
                if data:
                    data = data.decode('utf-8', 'ignore')
                    return self.authenticate(data)
                else:
                    return None
            else:  # It must be a new client.
                client, _ = ins.accept()
                self.inputs.append(client)
                return None
        elif ins == sys.stdin:  # Maybe its standard input?
            return sys.stdin.readline().strip()
        else:  # If not, assume file descriptor
            data = os.read(ins, 255).decode('utf-8', 'ignore')
            return data

    def message(self, message):
        """
            Used by other instances of this object to send a message.
        """
        self.sendLine(message)


class RelayFactory(protocol.Factory):
    protocol = Relay
    # A hashmap of previously seen addresses and their client.
    clients = {}
    # A mapping of public ids to private ids. Should be put into seperate file.
    authkeys = {}

    def __init__(self, istreams, authkeys=None):
        """
            Initializes the RelayFactory with a list of input streams and the authkeys.
        """
        if authkeys: self.authkeys = authkeys
        if isinstance(istreams, list):
            self.istreams = istreams
        else:
            self.istreams = [istreams]
        print("Server started")

    def buildProtocol(self, addr):
        """
            Creates clients for new connections and returning clients.
            :param addr: the address the client connected from.
            :return: the protocol that has been made.
        """
        addr = addr.host
        # Determine if we've seen this client before.
        if addr not in self.clients:
            print("New client", addr)
            self.clients[addr] = self.protocol(self.istreams)
            self.clients[addr].factory = self
        else:
            print("Reconnection from", addr)
        p = self.clients[addr]
        return p

    def stopFactory(self):
        """Used to close our input streams when factory is done."""
        for ins in self.istreams:
            if isinstance(ins, socket.socket):
                ins.close()


def main():
    """Configures and starts the RelayFactory."""
    authkeys = {'test': 'qwerty123'}

    # Authkey Setup
    try:
        for line in open("authkeys.key.txt"):
            authpair = line.strip().split(' ')
            authkeys[authpair[0]] = authpair[1]
    except Exception as e:
        print("WARN:", e)

    # Telnet Interface Setup
    host = ""
    port = 42420
    ins = []
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(4)
    ins.append(s)

    # FIFO Interface Setup
    s = os.open('input', os.O_RDONLY | os.O_NONBLOCK)
    ins.append(s)

    # Start factory.
    f = RelayFactory(ins, authkeys)
    reactor.listenTCP(42124, f)
    reactor.run()


if __name__ == '__main__':
    main()
