import yaml

from . import args
from . import config
from . import logger
from . import mesher

_LOGGER = logger.get_logger()


def main():
    cmd_args = args.CommandLineArgs()
    cfg = config.parse(cmd_args.config)
    _LOGGER.info(f'Config: {yaml.dump(cfg)}')

    mesh = mesher.create_mesh(cfg)
    _LOGGER.info('Mesh created')
    mesh.save()


if __name__ == '__main__':
    main()
