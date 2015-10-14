import time
from schedule import Heap
import plugins
from twisted.internet import reactor,protocol,endpoints,task
from twisted.protocols.basic import LineReceiver

__author__ = 'wstevens'

class IntercomProtocol(LineReceiver):

    def check(self):
        if not self.factory.heap.empty():
            run_time, cmd = self.factory.heap.peek()
            if run_time <= time.time():
                self.factory.heap.pop()
                cmd.act()

    def connectionMade(self):
        print("Connected successfully")
        c = task.LoopingCall(self.check)
        c.start(5.0)

    def lineReceived(self, line):
        if line:
            parts = line.decode('utf-8','ignore').split("|")
            if len(parts) >= 2:
                parts[0]=' '.join(parts[:-1])
                parts[1]=parts[-1]
                print(parts[1],"New Message Recieved: ",parts[0])
                sc = plugins.command.SayCommand(parts[0])
                self.factory.heap.push(float(parts[1]), sc)
    

class IntercomClientFactory(protocol.ClientFactory):
    protocol = IntercomProtocol
    heap = Heap()

    def clientConnectionFailed(self, connector, reason):
        print('connection failed:', reason.getErrorMessage())
        time.sleep(5)
        connector.disconnect()
        connector.connect()
    
    def clientConnectionLost(self, connector, reason):
        print('connection lost:', reason.getErrorMessage())
        connector.disconnect()
        connector.connect()

    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        return p

try:
    with open('server.txt') as f:
        server = f.read().strip()
except FileNotFoundError:
        server = 'localhost'

connector = reactor.connectTCP(server, 42124, IntercomClientFactory())
print('connecting to:',server)
reactor.run()

