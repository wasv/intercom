from asyncio import Lock
import pickle
import time
import plugins.command

__author__ = 'ahanes'


class Heap(object):

    def __init__(self):
        self.arr = []
        self.lock = Lock()

    def push(self, key, value):
        self.arr.append((key, value))
        index = len(self.arr) - 1
        while index > -1 and self.arr[int(index / 2)][0] > self.arr[index][0]:
            self.arr[int(index / 2)], self.arr[index] = self.arr[index], self.arr[int(index / 2)]
            index = int(index / 2)

    def peek(self):
        head = self.arr[0]
        return head

    def empty(self):
        e = len(self.arr) == 0
        return e

    def pop(self):
        top = self.arr[0]
        if len(self.arr) == 1:
            self.arr = []
        else:
            self.arr[0] = self.arr[-1]
            self.arr.pop()
            index = 0
            while index < len(self.arr):
                left = index * 2 + 1
                right = index * 2 + 2
                if len(self.arr) - 1 < left:
                    break
                elif len(self.arr) - 1 < right:
                    swap_index = left
                else:
                    swap_index = left if self.arr[left][0] < self.arr[right][0] else right
                if self.arr[swap_index][0] < self.arr[index][0]:
                    self.arr[swap_index], self.arr[index] = self.arr[index], self.arr[swap_index]
                    index = swap_index
                else:
                    break
        return top
