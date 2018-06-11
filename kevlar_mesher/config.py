from typing import IO, List

from dataclasses import dataclass
from voluptuous import All, Length


@dataclass
class Task:
    name: str

    resolution: float
    diameter: float

    width: float
    weft_density: float

    length: float
    warp_density: float


@dataclass
class Config:
    out_dir: str
    tasks: List[Task]


def _get_schema():
    from voluptuous import Schema, Required, Range, Any

    positive_number = All(Any(int, float), Range(min=0, min_included=False))
    return Schema({
        Required('out_dir'): All(str, Length(min=1)),
        Required('tasks'): [Schema({
            Required('name'): All(str, Length(min=1)),
            Required('resolution'): positive_number,
            Required('diameter'): positive_number,
            Required('width'): positive_number,
            Required('weft_density'): positive_number,
            Required('length'): positive_number,
            Required('warp_density'): positive_number,
        })]
    })


_schema = _get_schema()


def parse(f: IO) -> Config:
    import yaml
    import jinja2

    templated_data = jinja2.Template(f.read()).render()

    data = yaml.load(templated_data)

    _schema(data)

    return Config(tasks=[
        Task(
            name=task['name'],
            resolution=task['resolution'],
            diameter=task['diameter'],

            width=task['width'],
            weft_density=task['weft_density'],

            length=task['length'],
            warp_density=task['warp_density'],
        ) for task in data['tasks']
    ], out_dir=data['out_dir'])
