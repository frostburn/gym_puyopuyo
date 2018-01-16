import random
from multiprocessing import Pool

from gym_puyopuyo.agent import tree_search_actions
from gym_puyopuyo.state import State


def benchmark(depth, threshold, factor):
    state = State(16, 8, 5, 3, tsu_rules=False)
    total_reward = 0
    for i in range(1000):
        if i % 100 == 0:
            print(i, "/ 1000")
        actions = tree_search_actions(state, depth, occupation_threshold=threshold, factor=factor)
        action = random.choice(actions)
        reward = state.step(*state.actions[action])
        total_reward += reward
        if reward < 0:
            return total_reward, True
    return total_reward, False


if __name__ == "__main__":
    argss = []
    for t in [0.7, 0.75, 0.8, 0.85]:
        for f in [15, 18, 20, 25]:
            argss.append((3, t, f))
    with Pool() as p:
        results = p.starmap(benchmark, argss)
    for result, args in zip(results, argss):
        reward, died = result
        if not died:
            print(reward, args)
