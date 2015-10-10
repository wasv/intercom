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
        l = task.LoopingCall(self.check)
        l.start(1.0)

    def lineReceived(self, line):
        parts = line.decode('utf-8','ignore').split("|")
        print(parts[0],"New Message Recieved: ",parts[1])
        sc = plugins.command.SayCommand(parts[1])
        self.heap.push(float(parts[0]), sc)

class IntercomClientFactory(protocol.ClientFactory):
    protocol = IntercomProtocol
    
    def clientConnectionFailed(self, connector, reason):
        connector.connect()
    
    def clientConnectionLost(self, connector, reason):
        print('connection lost:', reason.getErrorMessage())
        connector.connect()

reactor.connectTCP('localhost', 8000, IntercomClientFactory())
reactor.run()

