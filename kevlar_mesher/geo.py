import itertools
import math
from typing import List

from dataclasses import dataclass
from vtk import vtkDoubleArray, vtkPolyLine, vtkUnstructuredGrid, vtkPoints, vtkVector3

from . import logger

_LOGGER = logger.get_logger()


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
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2)

    @property
    def yaml(self):
        return dict(
            x=self.x,
            y=self.y,
            z=self.z,
        )

    @staticmethod
    def from_yaml(data) -> 'Vector':
        return Vector(
            x=data['x'],
            y=data['y'],
            z=data['z'],
        )


@dataclass
class Point:
    coords: Vector
    velocity: Vector = Vector(x=0, y=0, z=0)
    data: float = 0


@dataclass
class Fiber:
    points: List[Point]

    def shift(self, dp: Point) -> 'Fiber':
        return Fiber(points=[
            Point(coords=p.coords + dp.coords, data=p.data) for p in self.points
        ])


@dataclass
class Layer:
    fibers: List[Fiber]


@dataclass
class Mesh:
    weft: Layer
    warp: Layer

    def make_vtu_grid(self):
        all_points = vtkPoints()

        displacement = vtkDoubleArray()
        displacement.SetName('displacement')

        velocity = vtkDoubleArray()
        velocity.SetName('velocity')
        velocity.SetNumberOfComponents(3)

        ug = vtkUnstructuredGrid()
        ug.SetPoints(all_points)
        ug.GetPointData().SetScalars(displacement)
        ug.GetPointData().SetVectors(velocity)

        current_idx = 0
        for fiber in itertools.chain(self.weft.fibers, self.warp.fibers):
            polyline = vtkPolyLine()
            for point in fiber.points:
                all_points.InsertNextPoint(point.coords.x, point.coords.y, point.coords.z)
                polyline.GetPointIds().InsertNextId(current_idx)
                displacement.InsertNextValue(point.data)
                velocity.InsertNextTuple3(point.velocity.x, point.velocity.y, point.velocity.z)
                current_idx += 1

            ug.InsertNextCell(polyline.GetCellType(), polyline.GetPointIds())

        return ug
