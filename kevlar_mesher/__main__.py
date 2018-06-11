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

    for n, task in enumerate(cfg.tasks):
        _LOGGER.info(f'Processing task #{n}: {task.name}')
        mesh = mesher.create_mesh(task)
        _LOGGER.info('Mesh created')
        mesh.save(cfg.out_dir, task.name)


if __name__ == '__main__':
    main()
