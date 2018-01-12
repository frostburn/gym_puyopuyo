from __future__ import unicode_literals

import sys

import numpy as np
from gym.utils import seeding

from gym_puyopuyo import util
from gym_puyopuyo.field import BottomField, TallField

ALLOWED_HEIGHTS = (BottomField.HEIGHT, TallField.HEIGHT, 13)


class State(object):
    def __init__(self, height, width, num_layers, num_deals, tsu_rules=False, has_garbage=False):
        if height not in ALLOWED_HEIGHTS:
            raise NotImplementedError("Only heights {} supported".format(ALLOWED_HEIGHTS))
        if width > BottomField.WIDTH:
            raise NotImplementedError("Maximum width is {}".format(BottomField.WIDTH))
        if height == 13 and not tsu_rules:
            raise NotImplementedError("Height 13 only available with tsu ruleset")
        if tsu_rules and not height == 13:
            raise NotImplementedError("Tsu ruleset available only for height 13")
        if height == BottomField.HEIGHT:
            self.field = BottomField(num_layers, has_garbage=has_garbage)
        else:
            self.field = TallField(num_layers, tsu_rules=tsu_rules, has_garbage=has_garbage)
        self.width = width
        self.height = height
        self.num_deals = num_deals
        self.make_actions()
        self.seed()
        self.make_deals()

    @property
    def num_colors(self):
        return self.field.num_colors

    @property
    def num_layers(self):
        return self.field.num_layers

    @property
    def has_garbage(self):
        return self.field.has_garbage

    @property
    def tsu_rules(self):
        return getattr(self.field, "tsu_rules", False)

    @property
    def max_chain(self):
        return (self.width * self.height) // self.field.CLEAR_THRESHOLD

    @property
    def max_score(self):
        if isinstance(self.field, BottomField):
            return self.max_chain ** 2
        else:
            return self.max_chain * 999  # FIXME: This overshoots a lot

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return seed

    def reset(self):
        self.field.reset()
        self.make_deals()

    def render(self, outfile=sys.stdout):
        self.field.render(outfile, width=self.width, height=self.height)
        util.print_up(self.height, outfile=outfile)
        util.print_forward(2 * self.width + 4, outfile=outfile)
        remaining = self.height
        for deal in self.deals:
            for puyo in deal:
                util.print_puyo(puyo, outfile=outfile)
            util.print_back(4, outfile=outfile)
            util.print_down(2, outfile=outfile)
            remaining -= 2
        util.print_down(remaining, outfile=outfile)
        util.print_reset(outfile=outfile)
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
        for x in range(self.field.WIDTH - 1):
            self._validation_actions.append((x, 2))
        for x in range(self.field.WIDTH):
            self._validation_actions.append((x, 3))

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
        return np_state[:self.num_layers, (self.field.HEIGHT - self.height):, :self.width]

    def encode(self):
        return (self.encode_deals(), self.encode_field())

    def get_deal_stack(self, x, orientation):
        puyo_a, puyo_b = self.deals[0]
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

    def play_deal(self, x, orientation):
        self.make_deal()
        puyo_a, puyo_b = self.deals.pop(0)
        index = self._validation_actions.index((x, orientation))
        self.field._make_move(index, puyo_a, puyo_b)

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
        self.play_deal(x, orientation)
        return self.field.resolve()[0]

    def clone(self):
        clone = State(
            self.height,
            self.width,
            self.num_layers,
            self.num_deals,
            tsu_rules=self.tsu_rules,
            has_garbage=self.has_garbage
        )
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
