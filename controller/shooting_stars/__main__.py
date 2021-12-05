from time import sleep
import logging
from argparse import ArgumentParser

from .subscription import Subscription
from .device import Device
from .animation import run_animation, AnimationState

parser = ArgumentParser(prog='shooting_stars',
                        description='Christmas lights controller')
parser.add_argument('meteor_host',
                    help='host:port of Meteor server publishing lights state')
parser.add_argument('--log-level', dest='log_level', default='info', type=str)


def main():
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
    )

    lights_sub = Subscription(
        url=f'ws://{args.meteor_host}/websocket',
        name='lights',
    )
    lights_sub.start()

    try:
        animation_state = AnimationState()
        while True:
            try:
                run_animation(
                    device=Device.discover(),
                    lights=lights_sub.state,
                    animation_state=animation_state,
                )
            except Exception as ex:
                # Any exception will result in us reconnecting and
                # starting the animation again.
                logging.exception('Animation error')
                # Don't try to reconnect too often
                sleep(1)
    finally:
        # Stop the lights subscription thread.
        lights_sub.stop()


if __name__ == '__main__':
    main()
