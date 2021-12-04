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

# j = 0
# while True:
#     with BytesIO() as frame:
#         for i in range(LED_COUNT):
#             frame.write(struct.pack('>BBBB', *colours[(i + j) % len(colours)]))
#             # frame.write(struct.pack(
#             #     '>BBBB',
#             #     i,
#             #     (255 if j == 1 else 0),
#             #     (255 if j == 2 else 0),
#             #     (255 if j == 3 else 0),
#             # ))
#         frame.seek(0)
#         control.set_rt_frame_socket(frame, version=3)
#         #control.set_rt_frame_rest(frame)
#     sleep(1)
#     j = (j + 1) % len(colours)

import websocket
import json

def on_message(ws, message):
    log('msg', message)
    data = json.loads(message)

    msg = data.get('msg')

    if msg == 'failed':
        pass
    elif msg == 'connected':
        subscribe()
    elif msg == 'ready':
        pass
    elif msg == 'ping':
        pong = {'msg': 'pong'}
        if 'id' in data:
            pong['id'] = data['id']
        ws.send(json.dumps(pong))
    elif msg == 'nosub':
        # Handle error
        pass
    elif msg == 'added':
        pass
    elif msg == 'changed':
        pass
    elif msg == 'removed':
        pass
    else:
        # Ignore other msg types, which are either unknown or we don't
        # need to handle them.
        pass

def on_error(ws, error):
    log('err', error)

def on_close(ws, close_status_code, close_msg):
    log('close', close_status_code, close_msg)


def subscribe():
    ws.send(json.dumps({
        'msg': 'sub',
        'id': 'controller-sub-lights',
        'name': 'lights',
    }))

def connect(ws):
    ws.send(json.dumps({
        'msg': 'connect',
        'version': '1',
        'support': ['1'],
    }))

websocket.enableTrace(True)
ws = websocket.WebSocketApp(
    'ws://localhost:2500/websocket',
    on_open=connect,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)
ws.run_forever()
