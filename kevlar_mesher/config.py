from typing import IO

from dataclasses import dataclass


@dataclass
class Fiber:
    diameter: float
    density: int


@dataclass
class Layer:
    width: float
    weft: Fiber

    length: float
    warp: Fiber


@dataclass
class Config:
    resolution: int
    layer: Layer


def parse(f: IO) -> Config:
    import yaml
    data = yaml.load(f)

    return Config(
        resolution=data['resolution'],
        layer=Layer(
            length=data['layer']['length'],
            width=data['layer']['width'],
            weft=Fiber(
                diameter=data['layer']['weft']['diameter'],
                density=data['layer']['weft']['density']
            ),
            warp=Fiber(
                diameter=data['layer']['warp']['diameter'],
                density=data['layer']['warp']['density']
            ),
        ),
    )
