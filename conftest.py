from gym_puyopuyo import register
from gym_puyopuyo.env.endless import PuyoPuyoEndlessEnv
from gym_puyopuyo.env.versus import PuyoPuyoVersusEnv
from gym_puyopuyo.state import State

register()

State.TESTING = True
PuyoPuyoEndlessEnv.TESTING = True
PuyoPuyoVersusEnv.TESTING = True
