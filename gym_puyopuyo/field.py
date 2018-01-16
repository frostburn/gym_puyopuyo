from __future__ import unicode_literals

import sys

import numpy as np

import puyocore as core
from gym_puyopuyo import util
from gym_puyopuyo.bitboard import popcount


class BottomField(object):
    WIDTH = 8
    HEIGHT = 8
    CLEAR_THRESHOLD = 4

    def __init__(self, num_layers, has_garbage=False):
        self.num_layers = num_layers
        self.has_garbage = has_garbage
        if has_garbage:
            self.num_colors = num_layers - 1
        else:
            self.num_colors = num_layers
        self.reset()

    def reset(self):
        self.data = bytearray(8 * self.num_layers)

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
                if self.has_garbage:
                    garbage_puyo = self.data[i + self.HEIGHT * self.num_colors] & (1 << j)
                    if garbage_puyo:
                        util.print_color(6, outfile=outfile)
                        outfile.write("\u25ce ")
                        empty = False
                if empty:
                    outfile.write("\u00b7 ")
                util.print_reset(outfile=outfile)
            outfile.write("\n")

    def debug(self):
        core.bottom_render(self.data, self.num_layers)

    def handle_gravity(self):
        return core.bottom_handle_gravity(self.data, self.num_layers)

    def resolve(self):
        chain = core.bottom_resolve(self.data, self.num_layers, self.has_garbage)
        return (chain * chain, chain)

    def overlay(self, stack):
        layer = BottomField.from_list(stack, num_layers=self.num_layers)
        if layer.num_layers > self.num_layers:
            raise ValueError("Overlay has too many layers")
        mask = bytearray(8)
        for i, mine in enumerate(self.data):
            mask[i % 8] |= mine
        for i, (mine, yours) in enumerate(zip(self.data, layer.data)):
            self.data[i] = (mine | (yours & ~mask[i % 8]))

    def encode(self):
        data = core.bottom_encode(self.data, self.num_layers)
        return np.fromstring(data, dtype="int8").reshape(self.num_layers, self.HEIGHT, self.WIDTH)

    def _valid_moves(self, width=None):
        return core.bottom_valid_moves(self.data, self.num_layers)

    def _make_move(self, action, puyo_a, puyo_b):
        core.make_move(self.data, action, puyo_a, puyo_b)

    def to_list(self):
        result = []
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                puyo = None
                for k in range(self.num_layers):
                    if self.data[i + self.HEIGHT * k] & (1 << j):
                        puyo = k
                result.append(puyo)
        return result

    @property
    def popcount(self):
        return popcount(self.data)

    @property
    def sane(self):
        mask = bytearray(8)
        for i, line in enumerate(self.data):
            if line & mask[i % 8]:
                return False
            mask[i % 8] |= line
        return True

    @classmethod
    def from_list(cls, stack, num_layers=None, has_garbage=False):
        if len(stack) % cls.WIDTH != 0:
            raise ValueError("Puyos must form complete rows")
        if len(stack) > cls.WIDTH * cls.HEIGHT:
            raise ValueError("Too many puyos")
        if num_layers is None:
            num_layers = 0
            for puyo in stack:
                if puyo is not None:
                    num_layers = max(num_layers, puyo)
            num_layers += 1
        instance = cls(num_layers, has_garbage=has_garbage)
        for index, puyo in enumerate(stack):
            if puyo is not None:
                instance.data[index // cls.WIDTH + cls.HEIGHT * puyo] |= 1 << (index % cls.WIDTH)
        return instance


class TallField(object):
    WIDTH = 8
    HEIGHT = 16
    CLEAR_THRESHOLD = 4

    def __init__(self, num_layers, tsu_rules=False, has_garbage=False):
        if has_garbage:
            self.num_colors = num_layers - 1
        else:
            self.num_colors = num_layers
        self.num_layers = num_layers
        self.tsu_rules = tsu_rules
        self.has_garbage = has_garbage
        self.offset = 3 if tsu_rules else 0
        self.reset()

    def reset(self):
        self.data = bytearray(16 * self.num_layers)

    def render(self, outfile=sys.stdout, width=None, height=None):
        height = height or self.HEIGHT
        for i in range(self.HEIGHT - height, self.HEIGHT):
            row = i % 8
            offset = i // 8
            for j in range(width or self.WIDTH):
                empty = True
                for k in range(self.num_colors):
                    if self.data[row + 8 * k + 8 * self.num_layers * offset] & (1 << j):
                        if self.tsu_rules and i <= self.offset:
                            util.print_puyo(k + 7, outfile=outfile)
                        else:
                            util.print_puyo(k, outfile=outfile)
                        empty = False
                if self.has_garbage:
                    garbage_puyo = self.data[row + 8 * self.num_colors + 8 * self.num_layers * offset] & (1 << j)
                    if garbage_puyo:
                        if self.tsu_rules and i <= self.offset:
                            util.print_color(4, outfile=outfile)
                        else:
                            util.print_color(6, outfile=outfile)
                        outfile.write("\u25ce ")
                        empty = False
                if empty:
                    outfile.write("\u00b7 ")
                util.print_reset(outfile=outfile)
            outfile.write("\n")

    def debug(self):
        core.tall_render(self.data, self.num_layers)

    def handle_gravity(self):
        return core.tall_handle_gravity(self.data, self.num_layers)

    def resolve(self):
        return core.tall_resolve(self.data, self.num_layers, self.tsu_rules, self.has_garbage)

    def encode(self):
        data = core.tall_encode(self.data, self.num_layers)
        return np.fromstring(data, dtype="int8").reshape(self.num_layers, self.HEIGHT, self.WIDTH)

    def overlay(self, stack):
        layer = TallField.from_list(stack, num_layers=self.num_layers)
        if layer.num_layers > self.num_layers:
            raise ValueError("Overlay has too many layers")
        top_mask = bytearray(8)
        bottom_mask = bytearray(8)
        half = 8 * self.num_layers
        for i, mine in enumerate(self.data[:half]):
            top_mask[i % 8] |= mine
        for i, mine in enumerate(self.data[half:]):
            bottom_mask[i % 8] |= mine
        for i, (mine, yours) in enumerate(zip(self.data[:half], layer.data[:half])):
            self.data[i] = (mine | (yours & ~top_mask[i % 8]))
        for i, (mine, yours) in enumerate(zip(self.data[half:], layer.data[half:])):
            self.data[i + half] = (mine | (yours & ~bottom_mask[i % 8]))

    def _valid_moves(self, width):
        return core.tall_valid_moves(self.data, self.num_layers, width, self.tsu_rules)

    def _make_move(self, action, puyo_a, puyo_b):
        core.make_move(self.data, action, puyo_a, puyo_b)

    def to_list(self):
        result = []
        for i in range(self.HEIGHT):
            row = i % 8
            offset = i // 8
            for j in range(self.WIDTH):
                puyo = None
                for k in range(self.num_layers):
                    if self.data[row + 8 * k + 8 * self.num_layers * offset] & (1 << j):
                        puyo = k
                result.append(puyo)
        return result

    @property
    def popcount(self):
        return popcount(self.data)

    @property
    def sane(self):
        half = 8 * self.num_layers
        mask = bytearray(8)
        for i, line in enumerate(self.data[:half]):
            if line & mask[i % 8]:
                return False
            mask[i % 8] |= line
        mask = bytearray(8)
        for i, line in enumerate(self.data[half:]):
            if line & mask[i % 8]:
                return False
            mask[i % 8] |= line
        return True

    @classmethod
    def from_list(cls, stack, num_layers=None, tsu_rules=False, has_garbage=False):
        if len(stack) % cls.WIDTH != 0:
            raise ValueError("Puyos must form complete rows")
        if len(stack) > cls.WIDTH * cls.HEIGHT:
            raise ValueError("Too many puyos")
        if num_layers is None:
            num_layers = 0
            for puyo in stack:
                if puyo is not None:
                    num_layers = max(num_layers, puyo)
            num_layers += 1
        instance = cls(num_layers, tsu_rules=tsu_rules, has_garbage=has_garbage)
        for index, puyo in enumerate(stack):
            if puyo is not None:
                column = index % cls.WIDTH
                row = index // cls.WIDTH
                offset = row // 8
                row %= 8
                instance.data[row + 8 * puyo + 8 * num_layers * offset] |= 1 << column
        return instance
