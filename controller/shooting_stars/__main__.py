from time import sleep
import logging
from argparse import ArgumentParser

from .subscription import Subscription
from .device import Device, DeviceTimeout
from .animation import run_animation, AnimationState

parser = ArgumentParser(prog='shooting_stars',
                        description='Christmas lights controller')
parser.add_argument('meteor_url',
                    help='[ws|wss]://host:port of Meteor server publishing lights state')
parser.add_argument('--log-level', dest='log_level', default='info', type=str)

def main():
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
    )

    lights_sub = None
    device = None
    try:
        lights_sub = Subscription(
            url=f'{args.meteor_url}/websocket',
            name='lights',
        )
        lights_sub.start()
        animation_state = AnimationState()
        logging.info('Connecting to device...')
        try:
            device = Device.discover()
        except DeviceTimeout:
            # Don't verbosely log for known errors
            logging.warning('Device connection timed out...')
        logging.info('Connected to device...')
        if device is not None:
            device.start_monitor()
            run_animation(
                device=device,
                lights=lights_sub.state,
                animation_state=animation_state,
            )
    finally:
        # Clean up threads
        if lights_sub is not None:
            lights_sub.stop()
        if device is not None:
            device.stop_monitor()


if __name__ == '__main__':
    main()
