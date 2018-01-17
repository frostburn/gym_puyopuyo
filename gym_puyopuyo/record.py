from __future__ import unicode_literals

import json
from collections import deque
from random import random

import six


def write_record(file, initial_state, actions):
    """
    Write actions in a somewhat human readable JSON compatible format.
    """
    state = initial_state.clone()
    file.write("[[\n")
    for i, action in enumerate(actions):
        if isinstance(action, int):
            action = state.actions[action]
        clone = state.clone()
        stack = clone.get_deal_stack(*action)
        stack = ["0" if p is None else str(p + 1) for p in stack]
        file.write(", ".join(stack[:state.field.WIDTH][:state.width] + ["\n"]))
        file.write(", ".join(stack[state.field.WIDTH:][:state.width]) + "\n")
        if i == len(actions) - 1:
            file.write("]]")
        else:
            file.write("],[\n")
        state.step(*action)


def infer_deal_and_action(state, stack):
    deal = []
    for puyo in stack:
        if puyo is not None:
            deal.append(puyo)
    if random() < 0.5:
        deal = deal[::-1]
    x = [p is None for p in stack].index(False)
    orientation = None
    if stack[x] == deal[0]:
        if stack[x + 1] == deal[1]:
            orientation = 0
        elif stack[x + state.field.WIDTH] == deal[1]:
            orientation = 1
    else:
        if stack[x + 1] == deal[0]:
            orientation = 2
        elif stack[x + state.field.WIDTH] == deal[0]:
            orientation = 3
    if orientation is None:
        raise ValueError("Unable to infer action from stack {}".format(stack))
    return deal, (x, orientation)


def read_record(file, base_state, include_last=False):
    if isinstance(file, six.string_types):
        stacks = json.loads(file)
    else:
        stacks = json.load(file)
    if not stacks:
        return
    if len(stacks[0]) % base_state.width != 0:
        raise ValueError("Invalid record for width {}".format(base_state.width))
    if len(stacks[0]) != base_state.width * 2:
        raise NotImplementedError("Only height 2 stacks supported")

    state = base_state.clone()
    padding = [None] * (state.field.WIDTH - state.width)
    delayed = deque(maxlen=state.num_deals)
    for stack in stacks:
        stack = [None if p == 0 else p - 1 for p in stack]
        stack = stack[:state.width] + padding + stack[state.width:] + padding
        delayed.append(infer_deal_and_action(state, stack))
        if len(delayed) == state.num_deals:
            clone = state.clone()
            clone.deals = [d[0] for d in delayed]
            state.deals = clone.deals[:]
            deal, action = delayed.popleft()
            reward = state.step(*action)
            yield clone, action, reward
    # XXX: There should be a way to DRY this up
    while delayed:
        clone = state.clone()
        for i, (deal, action) in enumerate(delayed):
            clone.deals[i] = deal
        state.deals = clone.deals[:]
        deal, action = delayed.popleft()
        reward = state.step(*action)
        yield clone, action, reward

    if include_last:
        yield state, None, None
