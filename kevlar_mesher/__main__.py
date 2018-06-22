import yaml

from . import args
from . import config
from . import logger
from . import mesher
from . import solver
from . import writer

_LOGGER = logger.get_logger()


def main():
    cmd_args = args.CommandLineArgs()
    _LOGGER.info(f'Args: {cmd_args}')

    cfg = config.parse(cmd_args.config)
    _LOGGER.info(f'Config: {yaml.dump(cfg)}')

    for n, task in enumerate(cfg.tasks):
        _LOGGER.info(f'Processing task #{n+1}: {task.name}')
        mesh = mesher.create_mesh(task.mesh)
        _LOGGER.info('Mesh created')
        writer.save(mesh, cfg.out_dir, task.name)

        _LOGGER.info('Solving')
        results_generator = solver.solve(mesh, task.solver)
        for (idx, res) in enumerate(results_generator):
            writer.save(res, cfg.out_dir, f'{task.name}-{idx}')
        _LOGGER.info('Solved')


if __name__ == '__main__':
    main()
