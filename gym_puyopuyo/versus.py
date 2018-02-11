from __future__ import unicode_literals

import sys

import numpy as np
from gym.utils import seeding

from gym_puyopuyo import util
from gym_puyopuyo.state import State


class VersusState(State):
    def __init__(
        self,
        height,
        width,
        num_colors,
        num_deals=None,
        tsu_rules=False,
        deals=None,
        seed=None,
        step_bonus=0,
        all_clear_bonus=0,
        target_score=0,
        max_received_garbage=float("inf"),
    ):
        super(VersusState, self).__init__(
            height,
            width,
            num_colors + 1,
            num_deals=num_deals,
            tsu_rules=tsu_rules,
            deals=deals,
            seed=seed,
            has_garbage=True,
        )
        self.step_bonus = step_bonus
        self.all_clear_bonus = all_clear_bonus
        self.target_score = target_score
        self.max_received_garbage = max_received_garbage
        self.all_clear_pending = False
        self.step_score = 0
        self.chain_score = 0
        self.chain_number = 0
        self.pending_garbage = 0

    def reset(self):
        super(VersusState, self).reset()
        self.all_clear_pending = False
        self.step_score = 0
        self.chain_score = 0
        self.chain_number = 0
        self.pending_garbage = 0

    def clone(self):
        deals = self.deals[:]
        if self.num_deals is None:
            clone_deals = deals
        else:
            clone_deals = None
        clone = VersusState(
            self.height,
            self.width,
            self.num_colors,
            self.num_deals,
            tsu_rules=self.tsu_rules,
            deals=clone_deals,
            step_bonus=self.step_bonus,
            all_clear_bonus=self.all_clear_bonus,
            target_score=self.target_score,
            max_received_garbage=self.max_received_garbage,
        )
        clone.field.data[:] = self.field.data
        clone.deals = deals
        clone.all_clear_pending = self.all_clear_pending
        clone.step_score = self.step_score
        clone.chain_score = self.chain_score
        clone.chain_number = self.chain_number
        clone.pending_garbage = self.pending_garbage
        return clone

    def encode(self):
        return {
            "deals": self.encode_deals(),
            "field": self.encode_field(),
            "chain_number": self.chain_number,
            "pending_score": self.chain_score + self.step_score,
            "pending_garbage": self.pending_garbage,
            "all_clear": int(self.all_clear_pending),
        }

    def render(self, outfile=sys.stdout, in_place=False):
        if not in_place:
            for _ in range(self.height + 1):
                outfile.write("\n")
            util.print_up(self.height + 1, outfile=outfile)
        super(VersusState, self).render(outfile=outfile, in_place=True)
        status_text = "x{} c{} s{} p{} {}".format(
            self.chain_number,
            self.chain_score,
            self.step_score,
            self.pending_garbage,
            "!" if self.all_clear_pending else ""
        )
        outfile.write(status_text)
        util.print_down(1)
        util.print_back(len(status_text))

    def step(self, x, orientation):
        if not self.chain_number:
            if not self.deals:
                return 0, True
            if not self.validate_action(x, orientation):
                return 0, True

            self.play_deal(x, orientation)
            self.step_score += self.step_bonus

        had_chain = bool(self.chain_number)

        iterations = self.field.handle_gravity()
        fell = (iterations > 1)

        score = self.field.clear_groups(self.chain_number)
        if score:
            self.chain_score += score
            self.chain_number += 1

        released_garbage = 0
        if had_chain and not (fell or score):
            self.chain_number = 0

            self.chain_score += self.step_score
            self.step_score = 0

            if self.all_clear_pending:
                self.chain_score += self.all_clear_bonus
            self.all_clear_pending = False

            if self.chain_score >= 0:
                released_garbage, self.chain_score = divmod(self.chain_score, self.target_score)

            if not any(self.field.data):
                self.all_clear_pending = True

        if self.pending_garbage <= released_garbage:
            released_garbage -= self.pending_garbage
            self.pending_garbage = 0
        else:
            self.pending_garbage -= released_garbage
            released_garbage = 0

        if not self.chain_number:
            amount = self.pending_garbage
            if amount > self.max_received_garbage:
                amount = self.max_received_garbage
            self.pending_garbage -= amount
            self.add_garbage(amount)
            # Make garbage above the ghost line dissapear
            if self.tsu_rules:
                score, chain = self.field.resolve()
                assert (not score)

        if self.TESTING:
            assert (self.field.sane)
        return released_garbage, False

    def get_children(self, complete=False):
        result = []
        for action in self.actions:
            child = self.clone()
            released_garbage, done = child.step(*action)
            if done and complete:
                result.append((None, released_garbage))
            else:
                result.append((child, released_garbage))
        return result

    def get_action_mask(self):
        if self.chain_number:
            return np.ones(len(self.actions))
        return super(VersusState, self).get_action_mask()


class Game(object):
    def __init__(self, state_params, num_players=2, seed=None):
        _, self._seed = seeding.np_random(seed)
        self.game_over = False
        if state_params is None:
            return
        params = {"seed": self._seed}
        params.update(state_params)
        self.players = []
        for _ in range(num_players):
            self.players.append(VersusState(**params))

    def render(self, outfile=sys.stdout, in_place=False):
        height = self.players[0].height
        width = self.players[0].width
        if not in_place:
            for _ in range(height + 1):
                outfile.write("\n")
            util.print_up(height + 1, outfile=outfile)
        for player in self.players:
            player.render(outfile=outfile, in_place=True)
            util.print_up(height + 1)
            util.print_forward(2 * width + 9)
        util.print_down(height + 1)
        util.print_back(len(self.players) * (2 * width + 9))
        outfile.flush()

    def step(self, player_actions):
        """
        Return (result, garbage sent, done), tuple
        """
        if self.game_over:
            return 0, 0, True
        garbages = []
        dones = []
        for player, action in zip(self.players, player_actions):
            amount, done = player.step(*action)
            garbages.append(amount)
            dones.append(done)

        if any(dones):
            self.game_over = True
            player_1_lost = dones[0]
            an_opponent_lost = any(dones[1:])
            if player_1_lost:
                if an_opponent_lost:
                    return 0, 0, True
                return -1, 0, True
            return 1, 0, True

        offset = min(garbages)

        for i, amount in enumerate(garbages):
            amount -= offset
            for j, opponent in enumerate(self.players):
                if i == j:
                    continue
                opponent.pending_garbage += amount
        garbage_sent = garbages[0] - sum(garbages[1:])
        return 0, garbage_sent, False

    def seed(self, seed=None):
        seed = self.players[0].seed(seed)
        for player in self.players[1:]:
            player.seed(seed)
        return seed

    def reset(self):
        self.game_over = False
        self._seed = self.players[0].np_random.randint(0, 1234567890)
        for player in self.players:
            player.seed(self._seed)
            player.reset()

    def encode(self):
        return [p.encode() for p in self.players]

    def clone(self):
        clone = Game(None)
        clone.game_over = self.game_over
        clone.players = [p.clone() for p in self.players]
        return clone
