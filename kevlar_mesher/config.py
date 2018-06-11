from typing import IO, List

from dataclasses import dataclass


@dataclass
class Task:
    name: str

    resolution: int
    diameter: float

    width: float
    weft_density: int

    length: float
    warp_density: int


@dataclass
class Config:
    out_dir: str
    tasks: List[Task]


def parse(f: IO) -> Config:
    import yaml
    data = yaml.load(f)

    tasks = [
        Task(
            name=task['name'],
            resolution=task['resolution'],
            diameter=task['diameter'],

            width=task['width'],
            weft_density=task['weft_density'],

            length=task['length'],
            warp_density=task['warp_density'],
        ) for task in data['tasks']
    ]

    return Config(tasks=tasks, out_dir=data['out_dir'])
