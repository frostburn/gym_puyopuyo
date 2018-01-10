from random import shuffle

from gym_puyopuyo.util import permute


def test_permute():
    letters = list("hello world")
    permutation = list(range(len(letters)))
    shuffle(permutation)
    permute(letters, permutation)
    print(''.join(letters))
    assert (letters.count("l") == 3)
    assert (letters.count("o") == 2)
    assert (letters.count("h") == 1)
