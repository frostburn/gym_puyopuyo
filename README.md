# gym_puyopuyo
OpenAI Gym Environment for Puyo Puyo

This is a turn-based Puyo Puyo environment for https://github.com/openai/gym

There are four available environments small, wide, Tsu and large.

## Usage
```python
from gym_puyopuyo.env import register
from gym import make

register()

small_env = make("PuyoPuyoEndlessSmall-v2")

for i in range(10):
    small_env.step(small_env.action_space.sample())

small_env.render()
```
![Small environment rendered](https://user-images.githubusercontent.com/1253499/34639951-3c082b94-f2f2-11e7-88ad-92556be8baf2.png)
### Rendered representation
The playing field can be seen on the left.
Dots represent available empty space and colored circle represent puyos.
Puyos are cleared when they form groups of four or larger. Any puyos above the cleared groups fall down.
The clearing process repeats in a chain reaction. Longer chains give larger rewards.
The next available pieces are dealt to the right with the next piece to be played on top.
Each environment shows the next three available pieces.

### Actions
Unlike regular Puyo Puyo the pieces are not manouvered into place.
Instead each turn you will choose one of the discreet translations and rotations for the next piece.
![Small environment actions](https://user-images.githubusercontent.com/1253499/34640347-96e4e0f0-f2f9-11e7-9fe0-878f16793526.png)

There are `4 * width - 2` different actions to choose from.

### Stepping
The played piece is placed above the playing field where it will fall and all chain reactions are fully resolved.
Reward is chain length squared for the small and wide environments. Tsu and large environments use more complicated [scoring](https://puyonexus.com/wiki/Scoring).

### Observation encoding
The pieces to be played are encoded as a numpy arrays with `(n_colors, 3, 2)` shape.
The playing field is encoded as a numpy array with `(n_colors, heights, width)` shape.
An observations is a tuple of `(pieces, field)`.

### Tree search helpers
The underlying model is available through `env.unwrapped.get_root()`. See `test_env.py` for example usage in tree search.

## Environments
* Small
  - 8x3 grid with 3 different colors
* Wide
  - 8x8 grid with 4 different colors
* Tsu
  - 13x6 grid with 4 different colors and special handling for the top row
* Large
  - 16x8 grid with 5 different colors

### The Tsu environment
The Tsu environment is modeled closely after Puyo Puyo Tsu.
In contrast to Puyo Puyo Tsu there is no "death square" and play continues as long as there are empty squares available.
It has 12x6 grid with a special ghost row on top that isn't cleared when checking for groups.
It is also possible to play half moves where one of the puyos of the played pieces vanish due to going above the ghost row.

![Tsu environment rendered](https://user-images.githubusercontent.com/1253499/34640572-8e255518-f2fd-11e7-9748-f8ca48622bf0.png)

### Versus environments
All of the single player environments have corresponding versus modes where you play against a fixed reference opponent.
Each player has their own field and the pieces are dealt in the same sequence for both players.
The only mode of player interaction is through garbage puyos that falls from the top of the screen to the opponent's side.
The amount of garbage sent depends on the chain made in the same way as score does in single player mode.
If both players send garbage at the same time the difference is cancelled out.

![Tsu versus environment rendered](https://user-images.githubusercontent.com/1253499/36076058-10b6aa76-0f60-11e8-8807-eeaf4a010208.png)

### Observation encoding
Versus mode is encoded in the same way as single player but there are a few extra variables and the two sides are represented as `dict` objects.
The encoding is a two-tuple of
```python
{
    "deals": array,  # The upcoming pieces with shape (n_colors, 3, 2)
    "field": array,  # The playing field with shape (n_colors + 1, height, width)
    "chain_number": int,  # The number of links so far in the currently resolving chain reaction
    "pending_score": int,  # Score to be converted into garbage once the chain resolves
    "pending_garbage": int,  # Garbage to be received once the chain resolves. Will be offset by pending_score before landing.
    "all_clear": int,  # A boolean indicating if the player has an extra attack in reserve. Awarded by clearing the whole field.
}  # One dict per player
```


## Rolling your own opponent
If you wish to use your own agent as the opponent in a versus environment you can do it like this
```python
from gym_puyopuyo.env import ENV_PARAMS
from gym_puyopuyo.env.versus import PuyoPuyoVersusEnv

env = PuyoPuyoVersusEnv(my_agent, ENV_PARAMS["PuyoPuyoVersusTsu-v0"])
```

## Record format
The library implements a human-readable JSON format for recording and playing back games.

The data consists of a list of lists with each element corresponding to a puyo or empty space.
The inner lists each encode a piece and its position with gravity going downwards.
```json
[
    [
        0, 0, 1, 2, 0, 0,
        0, 0, 0, 0, 0, 0
    ],[
        0, 3, 0, 0, 0, 0,
        0, 1, 0, 0, 0, 0
    ],[
        0, 4, 4, 0, 0, 0,
        0, 0, 0, 0, 0, 0
    ]
]
```
```python
env = make("PuyoPuyoEndlessTsu-v2")
for observation, reward, done, info in env.read_record(data, include_last=True):
    state = info["state"]
    action = info["action"]
    state.render()
```
![Record rendered](https://user-images.githubusercontent.com/1253499/35029789-2e362ff4-fb65-11e7-9c07-2fc46ca9d38a.png)

## Reference agents
The library comes with reference agents for each of the environments.
Please note that they operate directly on the underlying model instead of the encoded observations.
```python
from gym.envs.registration import make

from gym_puyopuyo.agent import TsuTreeSearchAgent
from gym_puyopuyo.env import register

register()

agent = TsuTreeSearchAgent()

env = make("PuyoPuyoEndlessTsu-v2")

env.reset()
state = env.get_root()

for i in range(30):
    action = agent.get_action(state)
    _, _, done, info = env.step(action)
    state = info["state"]
    if done:
        break

env.render()
```
![Tsu agent rendered](https://user-images.githubusercontent.com/1253499/35029403-770b9edc-fb63-11e7-8859-15a775bc6a68.png)

The core is written in C for optimal performance.
See the [Wiki](https://github.com/frostburn/gym_puyopuyo/wiki) for implementation details
