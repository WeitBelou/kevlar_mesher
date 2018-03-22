from typing import IO

from dataclasses import dataclass


@dataclass
class Config:
    resolution: int
    diameter: float

    width: float
    weft_density: int

    length: float
    warp_density: int


def parse(f: IO) -> Config:
    import yaml
    data = yaml.load(f)

    return Config(
        resolution=data['resolution'],
        diameter=data['diameter'],

        width=data['width'],
        weft_density=data['weft_density'],

        length=data['length'],
        warp_density=data['warp_density'],
    )
