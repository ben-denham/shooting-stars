import websocket
import json
import logging
from time import monotonic, sleep
from threading import Thread

# Useful for debugging:
# websocket.enableTrace(True)

IMMEDIATE_FAILURE_SECONDS = 10


def del_if_exists(dictionary, key):
    try:
        del dictionary[key]
    except KeyError:
        pass


class Subscription:
    """Subscribe to lights data via Meteor's DDP protocol:
    https://github.com/meteor/meteor/blob/devel/packages/ddp/DDP.md
    and based on https://github.com/hharnisc/python-ddp/blob/master/DDPClient.py
    """

    def __init__(self, *, url, name):
        self.url = url
        self.name = name
        self.state = {}
        self.stopped = True
        self.sub_id = 0
        self.ws = None

    def start(self):
        """Run the subscription in a new thread"""
        sub_thread = Thread(target=self.run)
        sub_thread.start()

    def stop(self):
        """Can be called to stop the subscription."""
        self.stopped = True
        if self.ws:
            self.ws.close()

    def run(self):
        """Run the websocket listener, restarting with exponential backoff if
        the websocket closes."""
        self.stopped = False
        retry_delay_seconds = 1
        while True:
            attempt_start = monotonic()
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )
            self.ws.run_forever()
            logging.warning('Websocket closed')

            if self.stopped:
                break

            # Exponential backoff for immediate failures.
            if (monotonic() - attempt_start) < IMMEDIATE_FAILURE_SECONDS:
                retry_delay_seconds *= 2
                logging.warning(f'Waiting {retry_delay_seconds} seconds before restarting websocket')
                sleep(retry_delay_seconds)
            else:
                retry_delay_seconds = 1

            logging.warning('Restarting websocket')

    def send(self, ws, data):
        ws.send(json.dumps(data))

    def on_open(self, ws):
        """Send initial message to connect to Meteor."""
        self.send(ws, {
            'msg': 'connect',
            'version': '1',
            'support': ['1'],
        })

    def on_message(self, ws, message):
        """Handle incoming messages from the server."""
        data = json.loads(message)
        msg = data.get('msg')

        if msg == 'failed':
            logging.error(f'Subscription connection failure')
        elif msg == 'connected':
            self.sub_id += 1
            self.send(ws, {
                'msg': 'sub',
                'id': f'controller-sub-{self.name}-{self.sub_id}',
                'name': self.name,
            })
        elif msg == 'nosub':
            # Handle error and close the websocket to restart
            logging.error(f'Subscription error: {data["error"]}')
            ws.close()
        elif msg == 'added':
            if data['collection'] == self.name:
                item_id = data['id']
                self.state[item_id] = data['fields']
        elif msg == 'changed':
            if data['collection'] == self.name:
                item_id = data['id']
                if item_id in self.state:
                    self.state[item_id].update(data.get('fields', {}))
                    for field in data.get('cleared', []):
                        del_if_exists(self.state[item_id], field)
        elif msg == 'removed':
            if data['collection'] == self.name:
                del_if_exists(self.state, data['id'])
        elif msg == 'ping':
            pong = {'msg': 'pong'}
            if 'id' in data:
                pong['id'] = data['id']
            self.send(ws, pong)
        else:
            # Ignore other msg types, which are either unrecognised or
            # we don't need to handle them.
            pass

    def on_error(self, ws, error):
        """Log errors and close the websocket to restart."""
        logging.error(f'Subscription error: {error}')
        ws.close()

    def on_close(self, ws, close_status_code, close_message):
        """Log closures. This is not guaranteed to be called on every close
        (see: https://websocket-client.readthedocs.io/en/latest/threading.html)"""
        logging.error(f'Subscription closed: code: {close_status_code}, message: {close_message}')
