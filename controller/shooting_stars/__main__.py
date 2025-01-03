from time import sleep
import logging
from argparse import ArgumentParser

from .subscription import Subscription
from .device import Device
from .animation import run_animation, AnimationState
from .blocks import BlocksTrainer, run_blocks
from .cone import run_cone
from .presence import run_presence

ACTIVITIES = ['lights', 'blocks', 'cone', 'presence']

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

        device = Device(device_id=args.twinkly_device_id)
        device.start_monitor()

        animation_state = AnimationState()
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

        pictures_sub = Subscription(
            url=f'{args.meteor_url}/websocket',
            name='pictures',
            token=args.meteor_token,
        )
        pictures_sub.start()

        device = Device(device_id=args.twinkly_device_id)
        device.start_monitor()

        trainer = BlocksTrainer()
        trainer.start()

        run_blocks(
            device=device,
            inputs_sub=inputs_sub,
            pictures_sub=pictures_sub,
            trainer=trainer,
        )
    finally:
        # Clean up threads
        if inputs_sub is not None:
            inputs_sub.stop()
        if pictures_sub is not None:
            pictures_sub.stop()
        if device is not None:
            device.stop_monitor()
        if trainer is not None:
            trainer.stop()


def cone_activity(args):
    paint_sub = None
    device = None
    try:
        paint_sub = Subscription(
            url=f'{args.meteor_url}/websocket',
            name='paint',
            token=args.meteor_token,
        )
        paint_sub.start()

        device = Device(device_id=args.twinkly_device_id)
        device.start_monitor()

        run_cone(
            device=device,
            paint_sub=paint_sub,
        )
    finally:
        # Clean up threads
        if paint_sub is not None:
            paint_sub.stop()
        if device is not None:
            device.stop_monitor()


def presence_activity(args):
    device = None
    try:
        presence_sub = Subscription(
            url=f'{args.meteor_url}/websocket',
            name='presence',
            token=args.meteor_token,
            sub_param_list=[
                args.meteor_token,
            ]
        )
        presence_sub.start()

        device = Device(device_id=args.twinkly_device_id)
        device.start_monitor()

        run_presence(
            device=device,
            presence_sub=presence_sub,
        )
    finally:
        # Clean up threads
        if presence_sub is not None:
            presence_sub.stop()
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
    elif args.activity == 'cone':
        cone_activity(args)
    elif args.activity == 'presence':
        presence_activity(args)
    else:
        logging.error(f'Unrecognised activity: {args.activity}')


if __name__ == '__main__':
    main()
