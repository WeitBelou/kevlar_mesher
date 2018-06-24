import itertools
from typing import List

import vtk
from dataclasses import dataclass


@dataclass
class Vector:
    x: float
    y: float
    z: float

    def __add__(self, other: 'Vector') -> 'Vector':
        return Vector(
            x=self.x + other.x,
            y=self.y + other.y,
            z=self.z + other.z,
        )

    def __mul__(self, c: float) -> 'Vector':
        return Vector(
            x=self.x * c,
            y=self.y * c,
            z=self.z * c,
        )

    def dist(self, other: 'Vector') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5


@dataclass
class Point:
    coords: Vector
    data: float = 0


@dataclass
class Fiber:
    points: List[Point]

    def shift(self, dp: Point) -> 'Fiber':
        return Fiber(points=[
            Point(p.coords + dp.coords, p.data) for p in self.points
        ])


@dataclass
class Layer:
    fibers: List[Fiber]


@dataclass
class Mesh:
    weft: Layer
    warp: Layer

    def make_vtu_grid(self):
        all_points = vtk.vtkPoints()
        values = vtk.vtkDoubleArray()

        ug = vtk.vtkUnstructuredGrid()
        ug.SetPoints(all_points)
        ug.GetPointData().SetScalars(values)

        current_idx = 0
        for fiber in itertools.chain(self.weft.fibers, self.warp.fibers):
            polyline = vtk.vtkPolyLine()
            for point in fiber.points:
                all_points.InsertNextPoint(point.coords.x, point.coords.y, point.coords.z)
                polyline.GetPointIds().InsertNextId(current_idx)
                values.InsertNextValue(point.data)
                current_idx += 1

            ug.InsertNextCell(polyline.GetCellType(), polyline.GetPointIds())

        return ug
