import threading
import traceback
import time
from io import StringIO
import queue
import sys
from xmodem import XMODEM

class FakeIO(object):
    streams = [queue.Queue(), queue.Queue()]
    stdin = []
    stdot = []
    delay = 0.01 # simulate modem delays

    def putc(self, data, q=0):
        for char in data:
            self.streams[1-q].put(char)
            print('PUT%d(0x%x)' % (q, char), end=' ')
            sys.stdout.flush()
        return len(data)

    def getc(self, size, q=0):
        data = []
        #traceback.print_stack()
        while size:
            try:
                char = self.streams[q].get()
                print('GET%d(0x%x)' % (q, char), end=' ')
                sys.stdout.flush()
                data.append(char)
                size -= 1
            except queue.Empty:
                return None
        print()
        bdata = bytearray(data)
        s = bytes(bdata).decode('utf-8')
        print(f"{s}")
        return s

class Client(threading.Thread):
    def __init__(self, io, server, filename):
        threading.Thread.__init__(self)
        self.io     = io
        self.server = server
        self.stream = open(filename, 'rb')

    def getc(self, data, timeout=0):
        return self.io.getc(data, 0)

    def putc(self, data, timeout=0):
        return self.io.putc(data, 0)

    def run(self):
        self.xmodem = XMODEM(self.getc, self.putc)
        print('c.send', self.xmodem.send(self.stream))

class Server(FakeIO, threading.Thread):
    def __init__(self, io):
        threading.Thread.__init__(self)
        self.io     = io
        self.stream = StringIO()

    def getc(self, data, timeout=0):
        return self.io.getc(data, 1)

    def putc(self, data, timeout=0):
        return self.io.putc(data, 1)

    def run(self):
        self.xmodem = XMODEM(self.getc, self.putc)
        print('s.recv', self.xmodem.recv(self.stream))
        print('got')
        print(self.stream.getvalue())

if __name__ == '__main__':
    i = FakeIO()
    s = Server(i)
    c = Client(i, s, sys.argv[1])
    s.start()
    c.start()
