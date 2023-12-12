import zmq
import xled.discover
import logging
import psutil

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


orig_pipe = xled.discover.pipe

def pipe_with_timeout(ctx):
    """Monkey-patch pipe() to include a timeout"""
    parent_socket, child_socket = orig_pipe(ctx)
    parent_socket.setsockopt(zmq.RCVTIMEO, 10)
    return parent_socket, child_socket

xled.discover.pipe = pipe_with_timeout


orig_interfaceagent_start = xled.discover.InterfaceAgent.start

def new_interfaceagent_start(self):
    orig_interfaceagent_start(self)
    self.loop.close()
    self.periodic_ping.close()

xled.discover.InterfaceAgent.start = new_interfaceagent_start


for i in range(10_000):
    f = open('foo.txt', 'w')
    print(i)
    try:
        xled.discover.discover()
    except Exception as ex:
        logging.exception('msg')
        if 'many open files' in str(ex):
            f.close()
            print(psutil.Process().open_files())
            break
