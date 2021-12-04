import xled
from io import BytesIO
import struct
import sys

def log(*args):
    print(*args, flush=True)


log('Running!')

device = xled.discover.discover()
control = xled.ControlInterface(device.ip_address, device.hw_address)
control.set_mode('rt')

info = control.get_device_info()
LED_COUNT = info['number_of_led']

from time import sleep

colours = [
    (255, 0, 0, 0),
    (0, 255, 0, 0),
    (0, 0, 255, 0),
    (0, 0, 0, 255),
]

j = 0
while True:
    with BytesIO() as frame:
        for i in range(LED_COUNT):
            frame.write(struct.pack('>BBBB', *colours[(i + j) % len(colours)]))
            # frame.write(struct.pack(
            #     '>BBBB',
            #     i,
            #     (255 if j == 1 else 0),
            #     (255 if j == 2 else 0),
            #     (255 if j == 3 else 0),
            # ))
        frame.seek(0)
        control.set_rt_frame_socket(frame, version=3)
        #control.set_rt_frame_rest(frame)
    sleep(1)
    j = (j + 1) % len(colours)
