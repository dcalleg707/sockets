import subprocess
import os, signal
import time
import atexit
import signal
import sys

def handler(signum, frame):
    # do the cleaning if necessary

    # log your data here
    with open('log.log', 'a') as fo:
        fo.write('Force quit on %s.\n' % signum)

    # force quit
    sys.exit(1)  # only 0 means "ok"
    

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

try:    
    p = subprocess.Popen("""notepad.exe""")
    # Some actions
    time.sleep(5)
finally:
    exit_handler()

def exit_handler():
    print(p.pid)
    os.kill(p.pid, signal.SIGTERM) 

atexit.register(exit_handler)



