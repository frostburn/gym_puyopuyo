from __future__ import unicode_literals

import sys

import numpy as np
from gym.utils import seeding

from gym_puyopuyo import util
from gym_puyopuyo.field import BottomField, TallField

ALLOWED_HEIGHTS = (BottomField.HEIGHT, TallField.HEIGHT, 13)


class State(object):
    TESTING = False

    def __init__(
        self,
        height,
        width,
        num_layers,
        num_deals=None,
        tsu_rules=False,
        has_garbage=False,
        deals=None,
        seed=None
    ):
        if height not in ALLOWED_HEIGHTS:
            raise NotImplementedError("Only heights {} supported".format(ALLOWED_HEIGHTS))
        if width > BottomField.WIDTH:
            raise NotImplementedError("Maximum width is {}".format(BottomField.WIDTH))
        if height == 13 and not tsu_rules:
            raise NotImplementedError("Height 13 only available with tsu ruleset")
        if tsu_rules and not height == 13:
            raise NotImplementedError("Tsu ruleset available only for height 13")
        if num_deals and deals:
            raise ValueError("Cannot use a partial number of fixed deals")

        if height == BottomField.HEIGHT:
            self.field = BottomField(num_layers, has_garbage=has_garbage)
        else:
            self.field = TallField(num_layers, tsu_rules=tsu_rules, has_garbage=has_garbage)
        self.width = width
        self.height = height
        self.num_deals = num_deals
        self.garbage_x = 0 if has_garbage else None
        self.make_actions()
        self.seed(seed)
        if deals is None:
            self.make_deals()
        else:
            self.deals = list(deals)

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
            return 10 * self.width * self.height * 999 * self.max_chain  # FIXME: This overshoots a lot

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return seed

    def reset(self):
        self.field.reset()
        self.make_deals()

    def render(self, outfile=sys.stdout, in_place=False):
        if not in_place:
            for _ in range(self.height):
                outfile.write("\n")
            util.print_up(self.height, outfile=outfile)
        self.field.render(outfile, width=self.width, height=self.height, in_place=True)
        util.print_up(self.height, outfile=outfile)
        util.print_forward(2 * self.width + 2, outfile=outfile)
        remaining = self.height
        for deal in self.deals[:self.height // 2]:
            for puyo in deal:
                util.print_puyo(puyo, outfile=outfile)
            util.print_back(4, outfile=outfile)
            util.print_down(2, outfile=outfile)
            remaining -= 2
        util.print_reset(outfile=outfile)
        util.print_down(remaining, outfile=outfile)
        util.print_back(2 * self.width + 2, outfile=outfile)
        outfile.flush()

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

    def add_garbage(self, amount):
        if not amount:
            return
        if not self.has_garbage:
            raise ValueError("This state doesn't support garbage")
        if amount < 0:
            raise ValueError("Cannot add negative amount of garbage")
        garbage = self.field.num_colors
        stack = []
        while amount:
            line = [None] * self.field.WIDTH
            while self.garbage_x < self.width and amount:
                line[self.garbage_x] = garbage
                self.garbage_x += 1
                amount -= 1
            if self.garbage_x >= self.width:
                self.garbage_x = 0
            stack = line + stack
        if len(stack) > self.field.WIDTH * self.field.HEIGHT:
            stack = [garbage] * (self.field.WIDTH * self.field.HEIGHT)
        self.field.overlay(stack)
        self.field.handle_gravity()

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

    def mirror(self):
        self.field.mirror()
        self.field.shift(self.width - self.field.WIDTH)

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
        if self.num_deals is not None:
            self.make_deal()
        puyo_a, puyo_b = self.deals.pop(0)
        index = self._validation_actions.index((x, orientation))
        self.field._make_move(index, puyo_a, puyo_b)

    def get_action_mask(self):
        result = np.zeros(len(self.actions))
        bitset = self.field._valid_moves(self.width)
        for i, (x, orientation) in enumerate(self.actions):
            index = self._validation_actions.index((x, orientation % 2))
            if bitset & (1 << index):
                result[i] = 1
        return result

    def validate_action(self, x, orientation):
        orientation %= 2
        if x + 1 - orientation >= self.width:
            return False
        bitset = self.field._valid_moves(self.width)
        index = self._validation_actions.index((x, orientation))
        return bool(bitset & (1 << index))

    def step(self, x, orientation):
        if not self.deals:
            return -1
        if not self.validate_action(x, orientation):
            return -1
        self.play_deal(x, orientation)
        reward = self.field.resolve()[0]
        if isinstance(self.field, TallField) and not any(self.field.data):
            reward += 8500
        if self.TESTING:
            assert (self.field.sane)
        return reward

    def clone(self):
        deals = self.deals[:]
        if self.num_deals is None:
            clone_deals = deals
        else:
            clone_deals = None
        clone = State(
            self.height,
            self.width,
            self.num_layers,
            self.num_deals,
            tsu_rules=self.tsu_rules,
            has_garbage=self.has_garbage,
            deals=clone_deals,
        )
        clone.field.data[:] = self.field.data
        clone.deals = deals
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

    def field_to_int(self):
        result = 0
        for y in range(self.field.HEIGHT - self.height, self.field.HEIGHT):
            for x in range(self.width):
                result *= self.num_layers + 1
                puyo = self.field.puyo_at(x, y)
                if puyo is not None:
                    result += puyo + 1
        return result

    def field_from_int(self, n):
        self.field.reset()
        for y in reversed(range(self.field.HEIGHT - self.height, self.field.HEIGHT)):
            for x in reversed(range(self.width)):
                n, puyo = divmod(n, self.num_layers + 1)
                if puyo > 0:
                    self.field._unsafe_set_puyo_at(x, y, puyo - 1)
