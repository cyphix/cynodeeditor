# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

from dataclasses import dataclass



# TODO: see if there is a way to 'auto' the detection of list, tuple, etc
# TODO: testing
@dataclass
class Point:
    x: int
    y: int


    @property
    def point(self):
        return (self.x, self.y)

    @point.setter
    def point(self, point_tuple):
        self.x = point_tuple[0]
        self.y = point_tuple[1]

    @property
    def to_list(self):
        return [self.x, self.y]

    @property
    def to_tuple(self):
        return (self.x, self.y)
