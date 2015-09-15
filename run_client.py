__author__ = 'ahanes'
import client.client

def update_heap(heap):
    return heap

if __name__ == '__main__':
    client.client.client([lambda x: print(x), update_heap])
