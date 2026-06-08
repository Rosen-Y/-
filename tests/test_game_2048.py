import random

from game_2048 import Game2048, key_to_action, render


class NoSpawnGame(Game2048):
    def add_random_tile(self) -> bool:
        return False


def test_merge_line_merges_each_pair_once():
    assert Game2048.merge_line([2, 2, 2, 2]) == ([4, 4, 0, 0], 8)
    assert Game2048.merge_line([2, 0, 2, 4]) == ([4, 4, 0, 0], 4)
    assert Game2048.merge_line([4, 4, 4, 0]) == ([8, 4, 0, 0], 8)


def test_move_left_updates_board_and_score_without_extra_spawn():
    game = NoSpawnGame(rng=random.Random(0))
    game.board = [
        [2, 2, 0, 0],
        [4, 0, 4, 4],
        [2, 4, 8, 16],
        [0, 0, 0, 0],
    ]

    assert game.move("left") is True
    assert game.board == [
        [4, 0, 0, 0],
        [8, 4, 0, 0],
        [2, 4, 8, 16],
        [0, 0, 0, 0],
    ]
    assert game.score == 12


def test_can_move_detects_full_blocked_board():
    game = NoSpawnGame(rng=random.Random(0))
    game.board = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]

    assert game.can_move() is False


def test_key_to_action_supports_wasd_and_arrows():
    assert key_to_action("w") == "up"
    assert key_to_action("\x1b[C") == "right"
    assert key_to_action("Q") == "quit"


def test_render_contains_score_and_controls():
    game = NoSpawnGame(rng=random.Random(0))
    output = render(game)

    assert "分数: 0" in output
    assert "W/A/S/D" in output
