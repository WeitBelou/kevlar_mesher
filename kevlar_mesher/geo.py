import itertools
import pathlib
from typing import List

import vtk
from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.vx = self.vy = self.vz = 0

    def __add__(self, other: 'Point') -> 'Point':
        assert isinstance(other, Point)
        return Point(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def __mul__(self, c: 'float') -> 'Point':
        return Point(
            self.x * c,
            self.y * c,
            self.z * c,
        )

    def dist(self, other: 'Point') -> float:
        assert isinstance(other, Point)
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5


@dataclass
class Fiber:
    points: List[Point]

    def shift(self, dp: Point) -> 'Fiber':
        return Fiber(points=[
            p + dp for p in self.points
        ])


@dataclass
class Layer:
    fibers: List[Fiber]


@dataclass
class Mesh:
    weft: Layer
    warp: Layer

    def save(self, out_dir: str, name: str):
        out = pathlib.Path(out_dir)
        out.mkdir(exist_ok=True)
        out /= pathlib.Path(f'{name}.vtu')

        grid = self.make_grid()

        writer = vtk.vtkXMLDataSetWriter()
        writer.SetFileName(str(out.absolute()))
        writer.SetInputData(grid)
        writer.Write()

    def make_grid(self):
        ug = vtk.vtkUnstructuredGrid()
        all_points = vtk.vtkPoints()
        ug.SetPoints(all_points)

        current_idx = 0
        for fiber in itertools.chain(self.weft.fibers, self.warp.fibers):
            polyline = vtk.vtkPolyLine()
            for point in fiber.points:
                all_points.InsertNextPoint(point.x, point.y, point.z)
                polyline.GetPointIds().InsertNextId(current_idx)
                current_idx += 1

            ug.InsertNextCell(polyline.GetCellType(), polyline.GetPointIds())

        return ug
