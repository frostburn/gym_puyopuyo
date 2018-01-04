from __future__ import print_function

from gym_puyopuyo.state import BottomField, BottomState

_ = None
R = 0
G = 1
Y = 2
B = 3
P = 4
C = 5
W = 6


def test_action_mask():
    state = BottomState(8, 7, 2, 1)
    stack = [
        R, _, R, _, _, _, G, _,
    ]
    state.field = BottomField.from_list(stack, num_colors=state.num_colors)
    state.render()
    mask = state.get_action_mask()
    print(mask)
    assert (len(mask) == 6 + 6 + 7 + 7)
    for i, (x, orientation) in enumerate(state.actions):
        if x in (3, 4):
            assert (mask[i])
        elif orientation in (1, 3) and x in (1, 5):
            assert (mask[i])
        else:
            assert (not mask[i])
