#!/usr/bin/env python3
"""A small terminal version of the 2048 game.

Run with:
    python game_2048.py

Controls:
    W/A/S/D or arrow keys: move tiles
    R: restart after game over or win
    Q: quit
"""

from __future__ import annotations

import os
import random
import sys
from dataclasses import dataclass, field
from typing import Iterable, Literal

Direction = Literal["up", "down", "left", "right"]
Board = list[list[int]]

BOARD_SIZE = 4
TARGET_TILE = 2048


@dataclass
class Game2048:
    """Core 2048 game state and movement rules."""

    size: int = BOARD_SIZE
    rng: random.Random = field(default_factory=random.Random)
    board: Board = field(init=False)
    score: int = 0
    won: bool = False

    def __post_init__(self) -> None:
        if self.size < 2:
            raise ValueError("board size must be at least 2")
        self.reset()

    def reset(self) -> None:
        """Start a new game with two random tiles."""
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score = 0
        self.won = False
        self.add_random_tile()
        self.add_random_tile()

    @staticmethod
    def merge_line(line: Iterable[int]) -> tuple[list[int], int]:
        """Slide one row/column left and merge equal neighboring values once."""
        values = list(line)
        tiles = [value for value in values if value]
        merged: list[int] = []
        gained = 0
        index = 0

        while index < len(tiles):
            if index + 1 < len(tiles) and tiles[index] == tiles[index + 1]:
                combined = tiles[index] * 2
                merged.append(combined)
                gained += combined
                index += 2
            else:
                merged.append(tiles[index])
                index += 1

        merged.extend([0] * (len(values) - len(merged)))
        return merged, gained

    def empty_cells(self) -> list[tuple[int, int]]:
        """Return coordinates of all empty cells."""
        return [
            (row, col)
            for row in range(self.size)
            for col in range(self.size)
            if self.board[row][col] == 0
        ]

    def add_random_tile(self) -> bool:
        """Add a 2 tile (90%) or 4 tile (10%) to a random empty cell."""
        cells = self.empty_cells()
        if not cells:
            return False

        row, col = self.rng.choice(cells)
        self.board[row][col] = 4 if self.rng.random() < 0.1 else 2
        return True

    def move(self, direction: Direction) -> bool:
        """Move the board in one direction; return True when the board changed."""
        original = [row[:] for row in self.board]
        gained_total = 0

        if direction in {"left", "right"}:
            for row_index in range(self.size):
                row = self.board[row_index]
                working = list(reversed(row)) if direction == "right" else row
                merged, gained = self.merge_line(working)
                self.board[row_index] = list(reversed(merged)) if direction == "right" else merged
                gained_total += gained
        elif direction in {"up", "down"}:
            for col_index in range(self.size):
                column = [self.board[row][col_index] for row in range(self.size)]
                working = list(reversed(column)) if direction == "down" else column
                merged, gained = self.merge_line(working)
                if direction == "down":
                    merged = list(reversed(merged))
                for row_index, value in enumerate(merged):
                    self.board[row_index][col_index] = value
                gained_total += gained
        else:
            raise ValueError(f"unknown direction: {direction}")

        changed = self.board != original
        if changed:
            self.score += gained_total
            self.won = self.won or any(TARGET_TILE in row for row in self.board)
            self.add_random_tile()
        return changed

    def can_move(self) -> bool:
        """Return True while at least one legal move remains."""
        if self.empty_cells():
            return True

        for row in range(self.size):
            for col in range(self.size):
                value = self.board[row][col]
                if row + 1 < self.size and self.board[row + 1][col] == value:
                    return True
                if col + 1 < self.size and self.board[row][col + 1] == value:
                    return True
        return False


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def render(game: Game2048) -> str:
    """Build a printable board for the current game state."""
    width = max(4, len(str(max(max(row) for row in game.board))))
    horizontal = "+" + "+".join(["-" * (width + 2)] * game.size) + "+"
    lines = ["2048 Python 终端版", f"分数: {game.score}", horizontal]

    for row in game.board:
        cells = [str(value).center(width) if value else " ".center(width) for value in row]
        lines.append("| " + " | ".join(cells) + " |")
        lines.append(horizontal)

    lines.append("操作: W/A/S/D 或方向键移动，R 重新开始，Q 退出")
    if game.won:
        lines.append("恭喜！你合成了 2048。可以继续挑战更高分，或按 R 重新开始。")
    elif not game.can_move():
        lines.append("游戏结束！按 R 重新开始，或按 Q 退出。")
    return "\n".join(lines)


def read_key() -> str:
    """Read one key press on Windows or POSIX terminals."""
    if os.name == "nt":
        import msvcrt

        key = msvcrt.getwch()
        if key in {"\x00", "\xe0"}:
            key += msvcrt.getwch()
        return key

    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        first = sys.stdin.read(1)
        if first == "\x1b":
            return first + sys.stdin.read(2)
        return first
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def key_to_action(key: str) -> Direction | str | None:
    """Map keyboard input to a game direction or command."""
    mapping: dict[str, Direction | str] = {
        "w": "up",
        "W": "up",
        "\x1b[A": "up",
        "s": "down",
        "S": "down",
        "\x1b[B": "down",
        "a": "left",
        "A": "left",
        "\x1b[D": "left",
        "d": "right",
        "D": "right",
        "\x1b[C": "right",
        "r": "restart",
        "R": "restart",
        "q": "quit",
        "Q": "quit",
        "\x03": "quit",
    }
    return mapping.get(key)


def main() -> None:
    game = Game2048()

    while True:
        clear_screen()
        print(render(game))
        action = key_to_action(read_key())

        if action == "quit":
            print("\n再见！")
            return
        if action == "restart":
            game.reset()
        elif action in {"up", "down", "left", "right"} and game.can_move():
            game.move(action)  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
