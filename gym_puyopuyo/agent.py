import random

import numpy as np

import puyocore as core
from gym_puyopuyo.field import BottomField

GAMMA = 0.95
DEATH_VALUE = -10


def tree_search_actions(state, depth, factor=0.22, occupation_threshold=0.0):
    if not isinstance(state.field, BottomField):
        raise ValueError("Can only search bottom fields")
    colors = []
    for deal in state.deals[1:]:
        colors.extend(deal)

    action_mask = 0
    for action in state.actions:
        action_mask |= 1 << state._validation_actions.index(action)

    base_popcount = state.field.popcount
    prevent_chains = (base_popcount < occupation_threshold * state.width * state.height)

    best_indices = []
    best_score = DEATH_VALUE

    possible_indices = []
    possible_score = DEATH_VALUE
    for index, (child, score) in enumerate(state.get_children(True)):
        if not child:
            continue

        tree_score = core.bottom_tree_search(
            child.field.data,
            child.num_layers,
            child.has_garbage,
            action_mask,
            colors,
            depth - 1,
            factor
        )
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
    depth = 4
    factor = 0.22
    occupation_threshold = 0.4


class WideTreeSearchAgent(BaseTreeSearchAgent):
    depth = 3
    factor = 0.22
    occupation_threshold = 0.66


AGENTS = {
    "small": SmallTreeSearchAgent,
    "wide": WideTreeSearchAgent,
}
