import random

import numpy as np

import puyocore as core
from gym_puyopuyo.field import TallField

GAMMA = 0.95


def tree_search_actions(state, depth, factor=0.22, occupation_threshold=0.0):
    colors = []
    for deal in state.deals[1:]:
        colors.extend(deal)

    action_mask = 0
    for action in state.actions:
        action_mask |= 1 << state._validation_actions.index(action)

    search_args = [
        state.num_layers,
        state.has_garbage,
        action_mask,
        colors,
        depth - 1,
        factor,
    ]
    search_fun = core.bottom_tree_search
    if isinstance(state.field, TallField):
        search_args.insert(1, state.tsu_rules)
        search_args.insert(1, state.width)
        search_fun = core.tall_tree_search

    base_popcount = state.field.popcount
    prevent_chains = (base_popcount < occupation_threshold * state.width * state.height)

    best_indices = []
    best_score = float("-inf")

    possible_indices = []
    possible_score = float("-inf")
    for index, (child, score) in enumerate(state.get_children(True)):
        if not child:
            continue

        args = [child.field.data] + search_args
        tree_score = search_fun(*args)

        child_score = score + GAMMA * tree_score

        if prevent_chains and child.field.popcount < base_popcount:
            if child_score > possible_score:
                possible_indices = [index]
                possible_score = child_score
            elif child_score == possible_score:
                possible_indices.append(index)
        else:
            if child_score > best_score:
                best_indices = [index]
                best_score = child_score
            elif child_score == best_score:
                best_indices.append(index)
    return best_indices or possible_indices or [np.random.randint(0, len(state.actions))]


class BaseTreeSearchAgent(object):
    def __init__(self, returns_distribution=False):
        self.returns_distribution = returns_distribution

    def get_action(self, state):
        indices = tree_search_actions(state, self.depth, self.factor, self.occupation_threshold)
        if self.returns_distribution:
            dist = np.zeros(len(state.actions))
            for index in indices:
                dist[index] = 1
            dist /= dist.sum()
            return dist
        else:
            return random.choice(indices)


class SmallTreeSearchAgent(BaseTreeSearchAgent):
    """
    Average reward per step ~ 1.57
    """
    depth = 4
    factor = 0.22
    occupation_threshold = 0.4


class WideTreeSearchAgent(BaseTreeSearchAgent):
    """
    Average reward per step ~ 2.92
    """
    depth = 3
    factor = 0.22
    occupation_threshold = 0.66


class TsuTreeSearchAgent(BaseTreeSearchAgent):
    """
    Average reward per step ~ 1320
    """
    depth = 3
    factor = 20.0
    occupation_threshold = 0.7


class LargeTreeSearchAgent(BaseTreeSearchAgent):
    """
    Average reward per step ~ 2100
    """
    depth = 3
    factor = 15.0
    occupation_threshold = 0.75


AGENTS = {
    "small": SmallTreeSearchAgent,
    "wide": WideTreeSearchAgent,
    "tsu": TsuTreeSearchAgent,
    "large": LargeTreeSearchAgent,
}
