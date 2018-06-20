import itertools
import pathlib
from typing import Iterable, List

import vtk
from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float
    z: float

    def __add__(self, other: 'Point') -> 'Point':
        assert isinstance(other, Point)
        return Point(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )


@dataclass
class Fiber:
    points: Iterable[Point]

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
