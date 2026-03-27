"""Maze rendering: ASCII terminal and output file writer."""

import sys
from typing import Optional
from mazegen.generator import MazeGenerator, NORTH, EAST, SOUTH, WEST

# ANSI color codes
RESET  = "\033[0m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
WHITE  = "\033[37m"


def write_output(mg: MazeGenerator, path: str) -> None:
    """Write the maze to a file in the required hex format.

    Args:
        mg:   A generated MazeGenerator instance.
        path: Output file path.
    """
    hex_grid = mg.to_hex_grid()
    entry_x, entry_y = mg.entry
    exit_x, exit_y = mg.exit_

    with open(path, "w") as f:
        for row in hex_grid:
            f.write("".join(row) + "\n")
        f.write("\n")
        f.write(f"{entry_x},{entry_y}\n")
        f.write(f"{exit_x},{exit_y}\n")
        f.write("".join(mg.solution) + "\n")


class AsciiRenderer:
    """Interactive ASCII renderer for a generated maze.

    Supports toggling the solution path, changing wall colours,
    and re-generating the maze.

    Args:
        mg: A generated MazeGenerator instance.
    """

    WALL_COLORS = [WHITE, CYAN, YELLOW, RED, GREEN]
    COLOR_NAMES = ["white", "cyan", "yellow", "red", "green"]

    def __init__(self, mg: MazeGenerator) -> None:
        self.mg = mg
        self.show_path = False
        self.color_index = 0

    @property
    def wall_color(self) -> str:
        return self.WALL_COLORS[self.color_index]

    def render(self) -> str:
        """Return the maze as a multi-line ASCII string."""
        mg = self.mg
        w, h = mg.width, mg.height
        path_set: set[tuple[int, int]] = set()

        if self.show_path and mg.solution:
            x, y = mg.entry
            path_set.add((x, y))
            for step in mg.solution:
                if step == 'N': y -= 1
                elif step == 'S': y += 1
                elif step == 'E': x += 1
                elif step == 'W': x -= 1
                path_set.add((x, y))

        wc = self.wall_color
        lines: list[str] = []

        # top border
        lines.append(wc + "+" + ("+--" * w)[:-1] + "--+" + RESET)

        for y in range(h):
            # cell row
            row = wc + "|" + RESET
            for x in range(w):
                cell_char = self._cell_char(x, y, path_set)
                east_wall = wc + "|" + RESET if mg.wall_closed(x, y, EAST) else " "
                row += " " + cell_char + " " + east_wall
            lines.append(row)

            # bottom border row
            bottom = wc + "+" + RESET
            for x in range(w):
                south_wall = wc + "--" + RESET if mg.wall_closed(x, y, SOUTH) else "  "
                bottom += south_wall + wc + "+" + RESET
            lines.append(bottom)

        return "\n".join(lines)

    def _cell_char(
        self,
        x: int,
        y: int,
        path_set: set[tuple[int, int]],
    ) -> str:
        """Return the display character for a single cell."""
        if (x, y) == self.mg.entry:
            return GREEN + "E" + RESET
        if (x, y) == self.mg.exit_:
            return RED + "X" + RESET
        if (x, y) in path_set:
            return YELLOW + "·" + RESET
        return " "

    def run_interactive(self) -> None:
        """Start the interactive terminal loop."""
        self._print_help()
        while True:
            print(self.render())
            print()
            try:
                cmd = input("Command (h for help): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if cmd == "q":
                break
            elif cmd == "p":
                self.show_path = not self.show_path
            elif cmd == "c":
                self.color_index = (self.color_index + 1) % len(self.WALL_COLORS)
                print(f"Wall color: {self.COLOR_NAMES[self.color_index]}")
            elif cmd == "r":
                self.mg.seed = None  # new random seed
                try:
                    self.mg.generate()
                except ValueError as exc:
                    print(f"Warning: {exc}")
                self.show_path = False
            elif cmd == "h":
                self._print_help()
            else:
                print("Unknown command. Type 'h' for help.")

    @staticmethod
    def _print_help() -> None:
        print("  p = toggle path   c = cycle wall colour")
        print("  r = regenerate    q = quit")