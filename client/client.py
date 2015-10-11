import time
from schedule import Heap
import plugins
from twisted.internet import reactor,protocol,endpoints,task
from twisted.protocols.basic import LineReceiver

__author__ = 'wstevens'

class IntercomProtocol(LineReceiver):
    heap = Heap()

    def check(self):
        if not self.heap.empty():
            run_time, cmd = self.heap.peek()
            if run_time <= time.time():
                self.heap.pop()
                cmd.act()

    def __init__(self):
        c = task.LoopingCall(self.check)
        c.start(1.0)

    def connectionMade(self):
        h = task.LoopingCall(self.heartbeat)
        h.start(5.0)

    def lineReceived(self, line):
        if line:
            parts = line.decode('utf-8','ignore').split("|")
            if len(parts) >= 2:
                parts[1]=' '.join(parts[1:])
                print(parts[0],"New Message Recieved: ",parts[1])
                sc = plugins.command.SayCommand(parts[1])
                self.heap.push(float(parts[0]), sc)
    
    def heartbeat(self):
        self.sendLine("<3<3".encode('utf-8'))


class IntercomClientFactory(protocol.ClientFactory):
    protocol = IntercomProtocol
    
    def clientConnectionFailed(self, connector, reason):
        print('connection failed:', reason.getErrorMessage())
        time.sleep(5)
        connector.disconnect()
        connector.connect()
    
    def clientConnectionLost(self, connector, reason):
        print('connection lost:', reason.getErrorMessage())
        connector.disconnect()
        connector.connect()

try:
    with open('server.txt') as f:
        server = f.read().strip()
except FileNotFoundError:
        server = 'localhost'

connector = reactor.connectTCP(server, 42124, IntercomClientFactory())
print('connecting to:',server)
reactor.run()

