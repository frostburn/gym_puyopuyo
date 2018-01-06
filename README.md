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

The core is written in C for optimal performance.
See the [Wiki](https://github.com/frostburn/gym_puyopuyo/wiki) for implementation details
