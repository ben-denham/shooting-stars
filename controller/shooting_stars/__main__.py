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

    lights_sub = Subscription(
        url=f'{args.meteor_url}/websocket',
        name='lights',
    )
    lights_sub.start()

    try:
        animation_state = AnimationState()
        device = None
        while True:
            try:
                logging.info('Connecting to device...')
                device = Device.discover()
                logging.info('Connected to device...')
                device.start_monitor()
                run_animation(
                    device=device,
                    lights=lights_sub.state,
                    animation_state=animation_state,
                )
            except KeyboardInterrupt:
                raise
            # Any other exception will result in us reconnecting and
            # starting the animation again.
            except Exception as ex:
                # Don't verbosely log for known errors
                if isinstance(ex, DeviceTimeout):
                    logging.warning('Device connection timed out...')
                else:
                    logging.exception('Unhandled error')
                # Don't try to reconnect too often
                sleep(1)
            finally:
                # Clean up device monitor
                if device is not None:
                    device.stop_monitor()
    finally:
        # Stop the lights subscription thread.
        lights_sub.stop()


if __name__ == '__main__':
    main()
