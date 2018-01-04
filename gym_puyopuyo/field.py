from __future__ import unicode_literals

import sys

import puyocore as core
from gym_puyopuyo import util


def print_puyo(color, outfile=sys.stdout):
    util.print_color(
        (color % 7) + 1,
        bright=(1 + color // 7) % 2,
        outfile=outfile,
    )
    outfile.write("\u25cf ")


class TallField(object):
    WIDTH = 8
    HEIGHT = 16
    CLEAR_THRESHOLD = 4

    def __init__(self, num_colors):
        self.num_colors = num_colors
        self.reset()

    def reset(self):
        self.data = bytearray(16 * self.num_colors)

    def render(self, outfile=sys.stdout):
        for i in range(self.HEIGHT):
            row = i % 8
            offset = i // 8
            for j in range(self.WIDTH):
                empty = True
                for k in range(self.num_colors):
                    if self.data[row + 8 * k + 8 * self.num_colors * offset] & (1 << j):
                        print_puyo(k, outfile=outfile)
                        empty = False
                if empty:
                    outfile.write("\u00b7 ")
                util.print_reset(outfile=outfile)
            outfile.write("\n")

    def debug(self):
        core.tall_render(self.data, self.num_colors)

    def handle_gravity(self):
        return core.tall_handle_gravity(self.data, self.num_colors)

    def resolve(self, tsu_rules=False):
        return core.tall_resolve(self.data, self.num_colors, tsu_rules)

    def to_list(self):
        result = []
        for i in range(self.HEIGHT):
            row = i % 8
            offset = i // 8
            for j in range(self.WIDTH):
                puyo = None
                for k in range(self.num_colors):
                    if self.data[row + 8 * k + 8 * self.num_colors * offset] & (1 << j):
                        puyo = k
                result.append(puyo)
        return result

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
                column = index % cls.WIDTH
                row = index // cls.WIDTH
                offset = row // 8
                row %= 8
                instance.data[row + 8 * puyo + 8 * num_colors * offset] |= 1 << column
        return instance
