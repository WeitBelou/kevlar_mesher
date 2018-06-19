import ctypes


class Point(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_double),
        ('y', ctypes.c_double),
        ('z', ctypes.c_double),
    ]


class Fiber(ctypes.Structure):
    _fields_ = [
        ('points', ctypes.pointer(Point)),
        ('n_points', ctypes.c_size_t)
    ]


class Mesh(ctypes.Structure):
    _fields_ = [('fibers',),
                (1,)]


def solve(mesh):
    ctypes.c_byte()
