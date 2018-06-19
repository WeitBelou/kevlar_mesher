import ctypes

from . import logger

_LOGGER = logger.get_logger()

libsolver = ctypes.CDLL('/usr/lib/libsolver.so')


def solve():
    _LOGGER.info(f'dll: {libsolver}')
