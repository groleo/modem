import datetime
import glob
import os
import select
import shutil
import subprocess
import sys
import io
import tempfile
from modem import *

def run(modem='zmodem'):

    if modem.lower().startswith('xmodem'):
        pipe   = subprocess.Popen(['sz', '--xmodem', '--quiet', __file__],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        si, so = (pipe.stdin, pipe.stdout)

        stream = io.StringIO()

    elif modem.lower() == 'ymodem':
        pipe   = subprocess.Popen(['sz', '--ymodem', '--quiet', __file__],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        si, so = (pipe.stdin, pipe.stdout)

        stream = io.StringIO()

    elif modem.lower() == 'zmodem':
        if len(sys.argv) > 2:
            files = sys.argv[2:]
        else:
            files = [__file__]
        #pipe   = subprocess.Popen(['zmtx', '-d', '-v'] + files,
        cmd = ['sz', '--zmodem', '--try-8k'] + files
        print(f"{cmd}")
        pipe   = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        si, so = (pipe.stdin, pipe.stdout)

        stream = io.StringIO()

    def getc(size, timeout=3):
        data = so.read(size)
        return data

    def putc(data, timeout=3):
        w,t,f = select.select([], [si], [], timeout)
        if t:
            if isinstance(data, str):
                si.write(bytes(data,'utf-8'))
                size = len(data)
            elif isinstance(data, int):
                si.write(data.to_bytes(1,'little'))
                size = 1
            else:
                size = len(data)
                si.write(data)
            si.flush()
        else:
            size = None

        #print datetime.datetime.now(), 'putc(', repr(data), repr(size), ')'
        return size

    if modem.lower().startswith('xmodem'):
        xmodem = globals()[modem.upper()](getc, putc)
        nbytes = xmodem.recv(stream, retry=8)
        print('received', nbytes, 'bytes', file=sys.stderr)
        print(stream.getvalue(), file=sys.stderr)

    elif modem.lower() == 'ymodem':
        ymodem = globals()[modem.upper()](getc, putc)
        basedr = tempfile.mkdtemp()
        nfiles = ymodem.recv(basedr, retry=8)
        print('received', nfiles, 'files in', basedr, file=sys.stderr)
        print(subprocess.Popen(['ls', '-al', basedr],
            stdout=subprocess.PIPE).communicate()[0], file=sys.stderr)
        shutil.rmtree(basedr)

    elif modem.lower() == 'zmodem':
        zmodem = globals()[modem.upper()](getc, putc)
        basedr = tempfile.mkdtemp()
        nfiles = zmodem.recv(basedr, retry=8)
        print('received', nfiles, 'files in', basedr, file=sys.stderr)
        print(subprocess.Popen(['ls', '-al', basedr],
            stdout=subprocess.PIPE).communicate()[0], file=sys.stderr)
        print(subprocess.Popen(['md5sum'] + glob.glob(basedr+'/*'),
            stdout=subprocess.PIPE).communicate()[0], file=sys.stderr)
        shutil.rmtree(basedr)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for modem in sys.argv[1:]:
            run(modem.upper())
    else:
        for modem in ['ZMODEM']: #, 'YMODEM']:
            run(modem)
