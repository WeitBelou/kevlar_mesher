import yaml

from . import args
from . import config
from . import logger
from . import mesher
from . import solver

_LOGGER = logger.get_logger()


def main():
    cmd_args = args.CommandLineArgs()
    _LOGGER.info(f'Args: {cmd_args}')

    cfg = config.parse(cmd_args.config)
    _LOGGER.info(f'Config: {yaml.dump(cfg)}')

    for n, task in enumerate(cfg.tasks):
        _LOGGER.info(f'Processing task #{n+1}: {task.name}')
        mesh = mesher.create_mesh(task)
        _LOGGER.info('Mesh created')
        mesh.save(cfg.out_dir, task.name)

        _LOGGER.info('Solving')
        solver.solve()


if __name__ == '__main__':
    main()
