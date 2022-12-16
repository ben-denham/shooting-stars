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


class DeviceTimeout(Exception):
    pass


class Device:

    def __init__(self, *, ip_address, hw_address):
        self.control = xled.ControlInterface(ip_address, hw_address)
        self.control.set_mode('rt')
        self.connected = True
        self.monitor_thread = None
        self.monitor_stopped = False

    @classmethod
    def discover(cls, device_id):
        try:
            xled_device = xled.discover.discover(find_id=device_id, timeout=TIMEOUT_SECONDS)
        except zmq.error.Again as ex:
            if 'Resource temporarily unavailable' in str(ex):
                raise DeviceTimeout()
            raise ex
        return cls(
            ip_address=xled_device.ip_address,
            hw_address=xled_device.hw_address,
        )

    def start_monitor(self):
        """Run the subscription in a new thread"""
        if self.monitor_thread is not None:
            return

        self.monitor_stopped = False
        self.monitor_thread = Thread(target=self.run_monitor)
        self.monitor_thread.start()

    def stop_monitor(self):
        self.monitor_stopped = True
        self.monitor_thread = None

    def run_monitor(self, interval_seconds=5):
        while not self.monitor_stopped and self.connected:
            sleep(interval_seconds)
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

    def set_frame_array(self, array: np.ndarray):
        """array should have a row for each LED, and a column for each RGBW
        component, with integer values."""
        if not self.connected:
            raise RuntimeError('Device disconnected')

        if array.dtype != FRAME_DTYPE:
            raise ValueError('Invalid frame array')

        with BytesIO() as frame:
            # C-order writes each row sequentially
            array_bytes = array.tobytes(order='C')
            frame.write(array_bytes)
            frame.seek(0)
            self.control.set_rt_frame_socket(frame, version=3)
