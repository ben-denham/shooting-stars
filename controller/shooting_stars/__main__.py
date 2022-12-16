from time import sleep
import logging
from argparse import ArgumentParser

from .subscription import Subscription
from .device import Device, DeviceTimeout
from .animation import run_animation, AnimationState
from .blocks import run_blocks

ACTIVITIES = ['lights', 'blocks']

parser = ArgumentParser(prog='shooting_stars',
                        description='Christmas lights controller')
parser.add_argument('meteor_url',
                    help='[ws|wss]://host:port of Meteor server publishing lights state')
parser.add_argument('activity', choices=ACTIVITIES)
parser.add_argument('twinkly_device_id', type=str)
parser.add_argument('--meteor-token', dest='meteor_token', type=str)
parser.add_argument('--log-level', dest='log_level', default='info', type=str)


def lights_activity(args):
    lights_sub = None
    device = None
    try:
        lights_sub = Subscription(
            url=f'{args.meteor_url}/websocket',
            name='lights',
            token=args.meteor_token,
        )
        lights_sub.start()
        animation_state = AnimationState()
        logging.info('Connecting to device...')
        try:
            device = Device.discover(args.twinkly_device_id)
        except DeviceTimeout:
            # Don't verbosely log for known errors
            logging.warning('Device connection timed out...')
        if device is not None:
            logging.info('Connected to device...')
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


def blocks_activity(args):
    inputs_sub = None
    device = None
    try:
        inputs_sub = Subscription(
            url=f'{args.meteor_url}/websocket',
            name='blocksInputs',
            token=args.meteor_token,
        )
        inputs_sub.start()
        logging.info('Connecting to device...')
        try:
            device = Device.discover(args.twinkly_device_id)
        except DeviceTimeout:
            # Don't verbosely log for known errors
            logging.warning('Device connection timed out...')
        if device is not None:
            logging.info('Connected to device...')
            device.start_monitor()
            run_blocks(
                device=device,
                inputs_sub=inputs_sub,
            )
    finally:
        # Clean up threads
        if inputs_sub is not None:
            inputs_sub.stop()
        if device is not None:
            device.stop_monitor()


def main():
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
    )

    if args.activity == 'lights':
        lights_activity(args)
    elif args.activity == 'blocks':
        blocks_activity(args)
    else:
        logging.error(f'Unrecognised activity: {args.activity}')


if __name__ == '__main__':
    main()
