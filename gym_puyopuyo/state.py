from __future__ import unicode_literals

import sys

import numpy as np
from gym.utils import seeding

import puyocore as core
from gym_puyopuyo import util


def print_puyo(color, outfile=sys.stdout):
    util.print_color(
        (color % 7) + 1,
        bright=(1 + color // 7) % 2,
        outfile=outfile,
    )
    outfile.write("\u25cf ")


class BottomField(object):
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
                        print_puyo(k, outfile=outfile)
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
        return core.bottom_resolve(self.data, self.num_colors)

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


class BottomState(object):
    def __init__(self, height, width, num_colors, num_deals):
        if height != BottomField.HEIGHT:
            raise NotImplementedError("Only height {} supported".format(BottomField.HEIGHT))
        if width > BottomField.WIDTH:
            raise ValueError("Maximum width is {}".format(BottomField.WIDTH))
        self.field = BottomField(num_colors)
        self.width = width
        self.height = height
        self.num_colors = num_colors
        self.num_deals = num_deals
        self.make_actions()
        self.seed()
        self.make_deals()

    @property
    def max_chain(self):
        return self.width * self.height // self.field.CLEAR_THRESHOLD

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return seed

    def reset(self):
        self.field.reset()
        self.make_deals()

    def render(self, outfile=sys.stdout):
        self.field.render(outfile)
        util.print_up(self.field.HEIGHT)
        util.print_forward(2 * self.field.WIDTH + 4)
        remaining = self.field.HEIGHT
        for deal in self.deals:
            for puyo in deal:
                print_puyo(puyo)
            util.print_back(4)
            util.print_down(2)
            remaining -= 2
        util.print_down(remaining)
        util.print_reset()
        outfile.write("\n")

    def make_actions(self):
        self.actions = []
        for x in range(self.width):
            self.actions.append((x, 1))
            self.actions.append((x, 3))
        for x in range(self.width - 1):
            self.actions.append((x, 0))
            self.actions.append((x, 2))

        self._validation_actions = []
        for x in range(self.field.WIDTH - 1):
            self._validation_actions.append((x, 0))
        for x in range(self.field.WIDTH):
            self._validation_actions.append((x, 1))

    def make_deals(self):
        self.deals = []
        for _ in range(self.num_deals):
            self.make_deal()

    def make_deal(self):
        self.deals.append((
            self.np_random.randint(0, self.num_colors),
            self.np_random.randint(0, self.num_colors),
        ))

    def encode_deals(self):
        np_deals = np.zeros((self.num_colors, self.num_deals, 2))
        for i, deal in enumerate(self.deals):
            np_deals[deal[0]][i][0] = 1
            np_deals[deal[1]][i][1] = 1
        return np_deals

    def encode_field(self):
        np_state = self.field.encode()
        return np_state[:self.num_colors, (self.field.HEIGHT - self.height):, :self.width]

    def encode(self):
        return (self.encode_deals(), self.encode_field())

    def play_deal(self, x, orientation):
        self.make_deal()
        puyo_a, puyo_b = self.deals.pop(0)
        stack = [None] * (2 * self.field.WIDTH)
        if orientation == 0:
            stack[x] = puyo_a
            stack[x+1] = puyo_b
        elif orientation == 1:
            stack[x] = puyo_a
            stack[x + self.field.WIDTH] = puyo_b
        elif orientation == 2:
            stack[x] = puyo_b
            stack[x+1] = puyo_a
        elif orientation == 3:
            stack[x] = puyo_b
            stack[x + self.field.WIDTH] = puyo_a
        else:
            raise ValueError("Unknown orientation")
        return stack

    def get_action_mask(self):
        result = np.zeros(len(self.actions))
        bitset = self.field._valid_moves()
        for i, (x, orientation) in enumerate(self.actions):
            index = self._validation_actions.index((x, orientation % 2))
            if bitset & (1 << index):
                result[i] = 1
        return result

    def validate_action(self, x, orientation):
        orientation %= 2
        bitset = self.field._valid_moves()
        index = self._validation_actions.index((x, orientation))
        return bool(bitset & (1 << index))

    def step(self, x, orientation):
        if not self.validate_action(x, orientation):
            return -1
        stack = self.play_deal(x, orientation)
        self.field.overlay_unsafe(stack)
        return self.field.resolve()

    def clone(self):
        clone = BottomState(self.height, self.width, self.num_colors, self.num_deals)
        clone.field.data[:] = self.field.data
        clone.deals[:] = self.deals
        return clone

    def get_children(self, complete=False):
        result = []
        for action in self.actions:
            child = self.clone()
            score = child.step(*action)
            if score >= 0:
                result.append((child, score))
            elif complete:
                result.append((None, score))
        return result
