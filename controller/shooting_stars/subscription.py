from time import monotonic
from datetime import datetime
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


class PromiseException(Exception):
    pass


class Promise:

    def __init__(self):
        self.started = monotonic()
        self.completed = False
        self.error = None
        self.result = None

    def set_error(self, error):
        self.error = error
        self.completed = True

    def set_result(self, result):
        self.result = result
        self.completed = True

    def await_result(self, sleep_interval=1):
        while not self.completed:
            sleep(sleep_interval)
        if self.error is not None:
            raise PromiseException(self.error)
        return self.result


class Subscription:
    """Subscribe to lights data via Meteor's DDP protocol:
    https://github.com/meteor/meteor/blob/devel/packages/ddp/DDP.md
    and based on https://github.com/hharnisc/python-ddp/blob/master/DDPClient.py
    """

    def __init__(self, *, url, name, token, sub_param_list=None):
        self.url = url
        self.name = name
        self.ready = False
        self.state = {}
        self.stopped = True
        self.ws = None
        self._uniq_id = 0
        self.connection_attempts = 0
        self.token = token
        self.sub_param_list = sub_param_list
        self.call_promises = {}

    def _next_id(self):
        """Get the next id that will be sent to the server"""
        self._uniq_id += 1
        return str(self._uniq_id)

    def start(self):
        """Run the subscription in a new thread"""
        sub_thread = Thread(target=self.run)
        sub_thread.start()
        return datetime.now()

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
                # Never delay more than 1 minute
                retry_delay_seconds = min(retry_delay_seconds, 60)
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
            param_config = {}
            if self.sub_param_list is not None:
                param_config = {'params': self.sub_param_list}
            self.send(ws, {
                'msg': 'sub',
                'id': self._next_id(),
                'name': self.name,
                **param_config,
            })
            self.ready = True
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
        elif msg == 'result':
            call_id = data['id']
            promise = self.call_promises[call_id]
            error = data.get('error')
            if error is not None:
                promise.set_error(error)
                return
            result = data.get('result')
            promise.set_result(result)
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

    def call(self, method, params):
        """Call a Meteor method on the server."""
        call_id = self._next_id()
        self.call_promises[call_id] = Promise()
        self.send(self.ws, {
            'msg': 'method',
            'id': call_id,
            'method': method,
            'params': params,
        })
        return self.call_promises[call_id]
