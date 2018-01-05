from __future__ import unicode_literals

import sys

import numpy as np

import puyocore as core
from gym_puyopuyo import util


class BottomField(object):
    WIDTH = 8
    HEIGHT = 8
    CLEAR_THRESHOLD = 4

    def __init__(self, num_colors):
        self.num_colors = num_colors
        self.reset()

    def reset(self):
        self.data = bytearray(8 * self.num_colors)

    def render(self, outfile=sys.stdout, width=None, height=None):
        height = height or self.HEIGHT
        for i in range(self.HEIGHT - height, self.HEIGHT):
            for j in range(width or self.WIDTH):
                empty = True
                for k in range(self.num_colors):
                    puyo = self.data[i + self.HEIGHT * k] & (1 << j)
                    if puyo:
                        util.print_puyo(k, outfile=outfile)
                        empty = False
                if empty:
                    outfile.write("\u00b7 ")
                util.print_reset(outfile=outfile)
            outfile.write("\n")

    def debug(self):
        core.bottom_render(self.data, self.num_colors)

    def handle_gravity(self):
        return core.bottom_handle_gravity(self.data, self.num_colors)

    def resolve(self):
        chain = core.bottom_resolve(self.data, self.num_colors)
        return (chain * chain, chain)

    def overlay(self, stack):
        layer = BottomField.from_list(stack)
        if layer.num_colors > self.num_colors:
            raise ValueError("Overlay has too many colors")
        mask = bytearray(8)
        for i, mine in enumerate(self.data):
            mask[i % 8] |= mine
        for i, (mine, yours) in enumerate(zip(self.data, layer.data)):
            if mask[i % 8] & yours:
                return False
            self.data[i] = (mine | yours)
        return True

    def overlay_unsafe(self, stack):
        layer = BottomField.from_list(stack)
        for i, puyos in enumerate(layer.data):
            self.data[i] |= puyos

    def encode(self):
        data = core.bottom_encode(self.data, self.num_colors)
        return np.fromstring(data, dtype="int8").reshape(self.num_colors, self.HEIGHT, self.WIDTH)

    def _valid_moves(self):
        return core.bottom_valid_moves(self.data, self.num_colors)

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


class TallField(object):
    WIDTH = 8
    HEIGHT = 16
    CLEAR_THRESHOLD = 4

    def __init__(self, num_colors, tsu_rules=False):
        self.num_colors = num_colors
        self.tsu_rules = tsu_rules
        self.offset = 3 if tsu_rules else 0
        self.reset()

    def reset(self):
        self.data = bytearray(16 * self.num_colors)

    def render(self, outfile=sys.stdout, width=None, height=None):
        height = height or self.HEIGHT
        for i in range(self.HEIGHT - height, self.HEIGHT):
            row = i % 8
            offset = i // 8
            for j in range(width or self.WIDTH):
                empty = True
                for k in range(self.num_colors):
                    if self.data[row + 8 * k + 8 * self.num_colors * offset] & (1 << j):
                        if self.tsu_rules and i <= self.offset:
                            util.print_puyo(k + 7, outfile=outfile)
                        else:
                            util.print_puyo(k, outfile=outfile)
                        empty = False
                if empty:
                    outfile.write("\u00b7 ")
                util.print_reset(outfile=outfile)
            outfile.write("\n")

    def debug(self):
        core.tall_render(self.data, self.num_colors)

    def handle_gravity(self):
        return core.tall_handle_gravity(self.data, self.num_colors)

    def resolve(self):
        return core.tall_resolve(self.data, self.num_colors, self.tsu_rules)

    def encode(self):
        data = core.tall_encode(self.data, self.num_colors)
        return np.fromstring(data, dtype="int8").reshape(self.num_colors, self.HEIGHT, self.WIDTH)

    def overlay_unsafe(self, stack):
        layer = BottomField.from_list(stack)
        for i, puyos in enumerate(layer.data):
            self.data[i] |= puyos

    def _valid_moves(self):
        return core.tall_valid_moves(self.data, self.num_colors, self.tsu_rules)

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
    def from_list(cls, stack, num_colors=None, tsu_rules=False):
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
        instance = cls(num_colors, tsu_rules)
        for index, puyo in enumerate(stack):
            if puyo is not None:
                column = index % cls.WIDTH
                row = index // cls.WIDTH
                offset = row // 8
                row %= 8
                instance.data[row + 8 * puyo + 8 * num_colors * offset] |= 1 << column
        return instance
