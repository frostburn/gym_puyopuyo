from __future__ import unicode_literals

import sys

import numpy as np

import puyocore as core
from gym_puyopuyo.util import print_color, print_reset


class BottomState(object):
    WIDTH = 8
    HEIGHT = 8
    CLEAR_THRESHOLD = 4

    def __init__(self, num_colors):
        self.num_colors = num_colors
        self.reset()

    def reset(self):
        self.data = bytearray(8 * self.num_colors)

    def render(self, outfile=sys.stdout):
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                empty = True
                for k in range(self.num_colors):
                    puyo = self.data[i + self.HEIGHT * k] & (1 << j)
                    if puyo:
                        print_color(
                            (k % 7) + 1,
                            bright=(1 + k // 7) % 2,
                            outfile=outfile,
                        )
                        empty = False
                if empty:
                    outfile.write("\u00b7")
                else:
                    outfile.write("\u25cf")
                outfile.write(" ")
                print_reset(outfile=outfile)
            outfile.write("\n")

    def debug(self):
        core.bottom_render(self.data, self.num_colors)

    def handle_gravity(self):
        return core.bottom_handle_gravity(self.data, self.num_colors)

    def resolve(self):
        return core.bottom_resolve(self.data, self.num_colors)

    def encode(self):
        data = core.bottom_encode(self.data, self.num_colors)
        return np.fromstring(data, dtype="int8").reshape(self.num_colors, self.HEIGHT, self.WIDTH)

    def to_list(self):
        result = []
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                puyo = None
                for k in range(self.num_colors):
                    if self.data[i + self.HEIGHT * k] & (1 << j):
                        puyo = k
                result.append(puyo)
        return result

    def clone(self):
        clone = BottomState(self.num_colors)
        clone.data = self.data[:]
        return clone

    @classmethod
    def from_list(cls, stack, num_colors=None):
        if len(stack) % cls.WIDTH != 0:
            raise ValueError("Puyos must form complete rows")
        if len(stack) > cls.WIDTH * cls.HEIGHT:
            raise ValueError("Too many puyos")
        if num_colors is None:
            num_colors = 0
            for puyo in stack:
                if puyo is not None:
                    num_colors = max(num_colors, puyo)
            num_colors += 1
        instance = cls(num_colors)
        for index, puyo in enumerate(stack):
            if puyo is not None:
                instance.data[index // cls.WIDTH + cls.HEIGHT * puyo] |= 1 << (index % cls.WIDTH)
        return instance
