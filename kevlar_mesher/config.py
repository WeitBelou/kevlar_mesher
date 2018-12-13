from typing import IO, List

from voluptuous import All, Length

from dataclasses import dataclass

from . import geo, logger

_LOGGER = logger.get_logger()


@dataclass
class Mesh:
    resolution: float
    diameter: float

    width: float
    weft_density: float

    length: float
    warp_density: float

    @property
    def yaml(self):
        return dict(
            resolution=self.resolution,
            diameter=self.diameter,
            width=self.width,
            weft_density=self.weft_density,
            length=self.length,
            warp_density=self.warp_density,
        )

    @staticmethod
    def from_yaml(data) -> 'Mesh':
        return Mesh(
            resolution=data['resolution'],
            diameter=data['diameter'],

            width=data['width'],
            weft_density=data['weft_density'],

            length=data['length'],
            warp_density=data['warp_density'],
        )


@dataclass
class Pulse:
    radius: float
    amplitude: float
    center: geo.Vector

    @property
    def yaml(self):
        return dict(
            radius=self.radius,
            amplitude=self.amplitude,
            center=self.center.yaml,
        )

    @staticmethod
    def from_yaml(data) -> 'Pulse':
        return Pulse(
            radius=data['radius'],
            amplitude=data['amplitude'],
            center=geo.Vector.from_yaml(data['center'])
        )


@dataclass
class Solver:
    step: float
    n_steps: int
    pulse: Pulse
    collisions_enabled: bool

    @property
    def yaml(self):
        return dict(
            step=self.step,
            n_steps=self.n_steps,
            pulse=self.pulse.yaml,
            collisions_enabled=self.collisions_enabled,
        )

    @staticmethod
    def from_yaml(data) -> 'Solver':
        return Solver(
            step=data['step'],
            n_steps=data['n_steps'],
            pulse=Pulse.from_yaml(data['pulse']),
            collisions_enabled=data['collisions_enabled']
        )


@dataclass
class Task:
    name: str
    mesh: Mesh
    solver: Solver

    @property
    def yaml(self):
        return dict(
            name=self.name,
            mesh=self.mesh.yaml,
            solver=self.solver.yaml,
        )

    @staticmethod
    def from_yaml(data) -> 'Task':
        return Task(
            name=data['name'],
            mesh=Mesh.from_yaml(data['mesh']),
            solver=Solver.from_yaml(data['solver']),
        )


@dataclass
class Config:
    out_dir: str
    tasks: List[Task]

    @property
    def yaml(self):
        return dict(
            out_dir=self.out_dir,
            tasks=[task.yaml for task in self.tasks]
        )

    @staticmethod
    def from_yaml(data) -> 'Config':
        return Config(
            out_dir=data['out_dir'],
            tasks=[Task.from_yaml(task) for task in data['tasks']]
        )


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
                Required('n_steps'): All(int, Range(min=0, min_included=False, max=1000)),
                Required('pulse'): Schema({
                    Required('radius'): positive_number,
                    Required('amplitude'): positive_number,
                    Required('center'): Schema({
                        Required('x'): number,
                        Required('y'): number,
                        Required('z'): number,
                    })
                }),
                Required('collisions_enabled'): bool,
            })
        })]
    })


_schema = _get_schema()


def parse(f: IO) -> Config:
    import yaml
    import jinja2

    data = yaml.load(jinja2.Template(f.read()).render())

    _schema(data)

    return Config.from_yaml(data)
