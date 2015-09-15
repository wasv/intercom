import time
from client.schedule import Heap
import plugins

__author__ = 'ahanes'

def client(actions=[]):
    """
    Start client
    :param actions: Actions to run each second
    :return: None
    """
    sc = plugins.command.SayCommand("Hello, World")
    heap = Heap()
    heap.push(time.time() + 1, sc)
    while True:
        for action in actions:
            resp = action(heap)
            if isinstance(resp, Heap):
                heap = resp
        if not heap.empty():
            run_time, cmd = heap.peek()
            if run_time <= time.time():
                heap.pop()
                cmd.act()
        time.sleep(1)
