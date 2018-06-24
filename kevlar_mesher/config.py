from typing import IO, List

from dataclasses import dataclass
from voluptuous import All, Length

from . import geo
from . import logger

_LOGGER = logger.get_logger()


@dataclass
class Mesh:
    resolution: float
    diameter: float

    width: float
    weft_density: float

    length: float
    warp_density: float


@dataclass
class Pulse:
    radius: float
    amplitude: float
    center: geo.Point


@dataclass
class Solver:
    step: float
    n_steps: int
    pulse: Pulse


@dataclass
class Task:
    name: str
    mesh: Mesh
    solver: Solver


@dataclass
class Config:
    out_dir: str
    tasks: List[Task]


def _get_schema():
    from voluptuous import Schema, Required, Range, Any

    positive_number = All(Any(int, float), Range(min=0, min_included=False))
    number = Any(int, float)
    return Schema({
        Required('out_dir'): All(str, Length(min=1)),
        Required('tasks'): [Schema({
            Required('name'): All(str, Length(min=1)),
            Required('mesh'): Schema({
                Required('resolution'): positive_number,
                Required('diameter'): positive_number,
                Required('width'): positive_number,
                Required('weft_density'): positive_number,
                Required('length'): positive_number,
                Required('warp_density'): positive_number,
            }),
            Required('solver'): Schema({
                Required('step'): positive_number,
                Required('n_steps'): All(int, Range(min=0, min_included=False, max=10000)),
                Required('pulse'): Schema({
                    Required('radius'): positive_number,
                    Required('amplitude'): positive_number,
                    Required('center'): Schema({
                        Required('x'): number,
                        Required('y'): number,
                        Required('z'): number,
                    })
                })
            })
        })]
    })


_schema = _get_schema()


def parse(f: IO) -> Config:
    import yaml
    import jinja2

    data = yaml.load(jinja2.Template(f.read()).render())

    _schema(data)

    return Config(tasks=[
        Task(
            name=task['name'],
            mesh=Mesh(
                resolution=task['mesh']['resolution'],
                diameter=task['mesh']['diameter'],

                width=task['mesh']['width'],
                weft_density=task['mesh']['weft_density'],

                length=task['mesh']['length'],
                warp_density=task['mesh']['warp_density'],
            ),
            solver=Solver(
                step=task['solver']['step'],
                n_steps=task['solver']['n_steps'],
                pulse=Pulse(
                    radius=task['solver']['pulse']['radius'],
                    amplitude=task['solver']['pulse']['amplitude'],
                    center=geo.Point(
                        x=task['solver']['pulse']['center']['x'],
                        y=task['solver']['pulse']['center']['y'],
                        z=task['solver']['pulse']['center']['z'],
                    ),
                ),
            ),
        ) for task in data['tasks']
    ], out_dir=data['out_dir'])
