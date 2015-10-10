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
        print(time.time(),"New Message Recieved: ",line)
        sc = plugins.command.SayCommand(line)
        self.heap.push(time.time() + 5, sc)

class IntercomFactory(protocol.Factory):
    def buildProtocol(self,addr):
        return IntercomProtocol()

endpoints.serverFromString(reactor, "tcp:1234").listen(IntercomFactory())
reactor.run()

