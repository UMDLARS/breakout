import random

import pytest
import sys

from littlepython import Compiler

from CYLGame import GameLanguage, GameRunner
from CYLGame.Player import Room

from ..game import SpaceInvaders as Game


def get_fuzzing_seeds(new_seed_count=10):
    previous_bad_seeds = [3000701892487371629, 8579693467990630982, 1544972200648834169]
    return previous_bad_seeds + [random.randint(0, sys.maxsize) for _ in range(new_seed_count)]


@pytest.mark.parametrize("seed", get_fuzzing_seeds())
def test_run_for_playback(seed):
    # Make default player bot
    compiler = Compiler()
    bot = Game.default_prog_for_bot(GameLanguage.LITTLEPY)
    prog = compiler.compile(bot)
    room = Room([prog], seed=seed)

    runner = GameRunner(Game)
    runner.run(room, playback=True)


@pytest.mark.parametrize("seed", get_fuzzing_seeds())
def test_run_for_score(seed):
    # Make default player bot
    compiler = Compiler()
    bot = Game.default_prog_for_bot(GameLanguage.LITTLEPY)
    prog = compiler.compile(bot)
    room = Room([prog], seed=seed)

    runner = GameRunner(Game)
    runner.run(room, playback=False)


@pytest.mark.parametrize("prog,seed", [("""
func is_barrier(s) {
    if s is BARRIER_4 or s is BARRIER_3 or s is BARRIER_2 or s is BARRIER_1 {
        return s
    } else {
        return 0
    }
}

func is_invader(s) {
    if s is INVADER_0 or s is INVADER_2 or s is INVADER_1 {
        return s
    } else {
        return 0
    }
}

move = stay

if is_barrier(player_center) or is_invader(player_center) or is_invader(player_left) or is_invader(player_left_minus_one) or is_invader(player_right_plus_one) or player_center is MISSILE {
    move = fire
}
""", 8493132599199290480)])
def test_run_for_score_with_prog(prog, seed):
    # Make player bot
    compiler = Compiler()
    prog = compiler.compile(prog)
    room = Room([prog], seed=seed)

    runner = GameRunner(Game)
    runner.run(room, playback=False)
