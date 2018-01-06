# gym_puyopuyo
OpenAI Gym Environment for Puyo Puyo

This is a turn-based Puyo Puyo environment for https://github.com/openai/gym

There are four available environments small, wide, Tsu and large.

## Usage
```python
from gym_puyopuyo.env import register
from gym.envs.registration import make

register()

small_env = make("PuyoPuyoEndlessSmall-v0")

for i in range(10):
    small_env.step(small_env.action_space.sample())

small_env.render()
```
![Small env rendered](https://user-images.githubusercontent.com/1253499/34639951-3c082b94-f2f2-11e7-88ad-92556be8baf2.png)

The core is written in C for optimal performance.
