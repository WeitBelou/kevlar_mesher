import logging

from mpl_toolkits.mplot3d import Axes3D
Axes3D

import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass

from . import config

DIM = 3

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s'
)

LOGGER = logging.getLogger('mesher')
LOGGER.setLevel(logging.INFO)


@dataclass
class Mesh:
    weft: np.ndarray
    warp: np.ndarray

    def draw(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        for f in self.weft:
            ax.plot(f.transpose()[0], f.transpose()[1], f.transpose()[2], color='green')
        for f in self.warp:
            ax.plot(f.transpose()[0], f.transpose()[1], f.transpose()[2], color='red')
        plt.show()


def create_mesh(cfg: config.Config) -> Mesh:
    LOGGER.info('start meshing...')

    n_warp_fibers = int(cfg.width * cfg.warp_density)
    n_points_for_warp_fiber = int(cfg.length * cfg.resolution)

    warp = np.zeros(shape=(n_warp_fibers, n_points_for_warp_fiber, DIM))
    warp_fibers_diff = np.array([0, 1 / cfg.warp_density, 0])
    warp_points_diff = np.array([1 / cfg.resolution, 0, 0])
    for i in range(n_warp_fibers):
        for j in range(n_points_for_warp_fiber):
            warp[i][j] = i * warp_fibers_diff + j * warp_points_diff

    n_weft_fibers = int(cfg.length * cfg.weft_density)
    n_points_for_weft_fiber = int(cfg.width * cfg.resolution)

    weft = np.zeros(shape=(n_weft_fibers, n_points_for_weft_fiber, DIM))
    weft_fibers_diff = np.array([1 / cfg.weft_density, 0, 0])
    weft_points_diff = np.array([0, 1 / cfg.resolution, 0])
    for i in range(n_weft_fibers):
        for j in range(n_points_for_weft_fiber):
            weft[i][j] = i * weft_fibers_diff + j * weft_points_diff

    LOGGER.info('end meshing...')

    return Mesh(weft=weft, warp=warp)
