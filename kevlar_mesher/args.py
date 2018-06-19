import argparse

import logging

LOGGER = logging.getLogger(__name__)


class CommandLineArgs:
    def __init__(self):
        args = CommandLineArgs._parse_commandline_args()

        LOGGER.debug('CommandLine args: {}'.format(args))

        self.config = args.config

    @staticmethod
    def _parse_commandline_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='Generates mesh for fibers.'
        )

        parser.add_argument(
            '-c', '--config', dest='config', type=argparse.FileType('r', encoding='utf-8'),
            required=True, help='Path to config file.'
        )

        return parser.parse_args()

    def __repr__(self) -> str:
        return '<CommandLineArgs config={config}>'.format(config=self.config)
