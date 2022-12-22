from io import BytesIO
from time import sleep
from threading import Thread
import logging
import numpy as np
import xled
from requests.compat import urljoin
import zmq
from xled.response import ApplicationResponse

FRAME_DTYPE = np.ubyte
TIMEOUT_SECONDS = 10


orig_pipe = xled.discover.pipe

def pipe_with_timeout(ctx):
    """Monkey-patch pipe() to include a timeout"""
    parent_socket, child_socket = orig_pipe(ctx)
    parent_socket.setsockopt(zmq.RCVTIMEO, TIMEOUT_SECONDS * 1000)
    return parent_socket, child_socket

xled.discover.pipe = pipe_with_timeout


class DeviceDisconnected(Exception):
    pass


class Device:

    def __init__(self, *, device_id):
        self.device_id = device_id
        self.monitor_stopped = False
        self.connected = False
        self.control = None

    def start_monitor(self):
        """Run the subscription in a new thread"""
        monitor_thread = Thread(target=self.run_monitor)
        monitor_thread.start()

    def stop_monitor(self):
        self.monitor_stopped = True

    def reconnect(self):
        # Clear anything that may exist from a previous connection
        try:
            self.control._udpclient.close()
        except:
            pass

        xled_device = xled.discover.discover(find_id=self.device_id, timeout=TIMEOUT_SECONDS)
        self.control = xled.ControlInterface(xled_device.ip_address, xled_device.hw_address)
        self.control.set_mode('rt')

    def run_monitor(self, interval_seconds=5):
        while not self.monitor_stopped:
            sleep(interval_seconds)
            if self.connected:
                try:
                    # Same as self.control.check_status() but with timeout
                    status_url = urljoin(self.control.base_url, 'status')
                    response = self.control.session.get(status_url, timeout=TIMEOUT_SECONDS)
                    status = ApplicationResponse(response)
                    if status['code'] != 1000:
                        self.connected = False
                except:
                    logging.exception('Device check failed')
                    self.connected = False
            else:
                try:
                    self.reconnect()
                    self.connected = True
                except:
                    logging.exception('Device check failed')

    def set_frame_array(self, array: np.ndarray):
        """array should have a row for each LED, and a column for each RGBW
        component, with integer values."""
        if not self.connected:
            raise DeviceDisconnected()

        if array.dtype != FRAME_DTYPE:
            raise ValueError('Invalid frame array')

        with BytesIO() as frame:
            # C-order writes each row sequentially
            array_bytes = array.tobytes(order='C')
            frame.write(array_bytes)
            frame.seek(0)
            self.control.set_rt_frame_socket(frame, version=3)
