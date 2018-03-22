from typing import IO

from dataclasses import dataclass


@dataclass
class Weft:
    density: int


@dataclass
class Warp:
    density: int


@dataclass
class Fibers:
    diameter: float
    weft: Weft
    warp: Warp


@dataclass
class Layer:
    length: float
    width: float


@dataclass
class Config:
    resolution: int
    fibers: Fibers
    layer: Layer


def parse(f: IO) -> Config:
    import yaml
    data = yaml.load(f)

    return Config(
        resolution=data['resolution'],
        fibers=Fibers(
            diameter=data['fibers']['diameter'],
            weft=Weft(density=data['fibers']['weft']['density']),
            warp=Warp(density=data['fibers']['warp']['density']),
        ),
        layer=Layer(
            length=data['layer']['length'],
            width=data['layer']['width'],
        ),
    )
