from io import BytesIO
import numpy as np
import xled

class Device:

    def __init__(self, *, ip_address, hw_address):
        self.control = xled.ControlInterface(ip_address, hw_address)
        self.control.set_mode('rt')

    @classmethod
    def discover(cls, timeout_seconds=10):
        xled_device = xled.discover.discover(timeout=timeout_seconds)
        return cls(
            ip_address=xled_device.ip_address,
            hw_address=xled_device.hw_address,
        )

    def set_frame_array(self, array: np.ndarray):
        """array should have a row for each LED, and a column for each RGBW
        component, with integer values."""
        assert array.dtype == np.ubyte
        with BytesIO() as frame:
            # C-order writes each row sequentially
            array_bytes = array.tobytes(order='C')
            frame.write(array_bytes)
            frame.seek(0)
            self.control.set_rt_frame_socket(frame, version=3)
