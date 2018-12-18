import time
from itertools import islice

import yaml

from . import args, config, logger, mesher, solver, writer

_LOGGER = logger.get_logger()


def main():
    cmd_args = args.CommandLineArgs()
    _LOGGER.info(f'Args: {cmd_args}')

    cfg = config.parse(cmd_args.config)
    _LOGGER.info(f'Config: {yaml.safe_dump(cfg.yaml)}')

    for n, task in enumerate(cfg.tasks):
        start_time = time.monotonic()
        _LOGGER.info(f'Processing task #{n+1} of {len(cfg.tasks)}: {task.name}')
        mesh = mesher.create_mesh(task.mesh)
        _LOGGER.info('Mesh created')
        writer.save(mesh, cfg.out_dir, f'{task.name}_mesh')

        _LOGGER.info('Solving')
        results_generator = islice(solver.solve(mesh, task.solver), task.solver.n_steps)
        for (idx, res) in enumerate(results_generator):
            writer.save(res, cfg.out_dir, f'{task.name}-{idx:04d}')
            _LOGGER.info(f'Done step {idx+ 1:d} of {task.solver.n_steps:d}')
        _LOGGER.info(f'Solved, took {time.monotonic() - start_time:.2f}s')


if __name__ == '__main__':
    main()
