"""Maze generation module using the recursive backtracker (DFS) algorithm."""

import random
from collections import deque
from dataclasses import dataclass, field
from typing import Optional


# Wall bit positions
NORTH = 0  # bit 0
EAST  = 1  # bit 1
SOUTH = 2  # bit 2
WEST  = 3  # bit 3

OPPOSITE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
DELTA = {
    NORTH: (0, -1),
    EAST:  (1,  0),
    SOUTH: (0,  1),
    WEST:  (-1, 0),
}
DIR_CHAR = {NORTH: 'N', EAST: 'E', SOUTH: 'S', WEST: 'W'}


@dataclass
class Cell:
    """A single maze cell with a 4-bit wall bitmask.

    Bit 0 = North, 1 = East, 2 = South, 3 = West.
    A set bit means the wall is CLOSED.
    """
    walls: int = 0b1111  # all walls closed by default


@dataclass
class MazeGenerator:
    """Generates a 2-D maze using the recursive backtracker algorithm.

    Args:
        width:   Number of columns.
        height:  Number of rows.
        entry:   (x, y) of the entry cell.
        exit_:   (x, y) of the exit cell.
        perfect: If True, produce a perfect maze (one path between any two cells).
        seed:    Optional RNG seed for reproducibility.

    Example::

        mg = MazeGenerator(width=20, height=15,
                           entry=(0, 0), exit_=(19, 14),
                           perfect=True, seed=42)
        mg.generate()
        print(mg.solution)         # list of 'N'/'E'/'S'/'W' steps
        print(mg.grid[0][0].walls) # bitmask for cell (0, 0)
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    perfect: bool = True
    seed: Optional[int] = None
    grid: list[list[Cell]] = field(default_factory=list, init=False)
    solution: list[str] = field(default_factory=list, init=False)
    _rng: random.Random = field(default_factory=random.Random, init=False)

    def generate(self) -> None:
        """Generate the maze in-place, then solve it."""
        self._rng.seed(self.seed)
        self._init_grid()
        self._carve_passages()
        if not self.perfect:
            self._add_extra_passages()
        self._embed_42()
        self._solve()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_grid(self) -> None:
        """Create a fresh grid of fully-walled cells."""
        self.grid = [
            [Cell() for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def _open_wall(self, x: int, y: int, direction: int) -> None:
        """Remove the wall between (x, y) and its neighbour in `direction`."""
        dx, dy = DELTA[direction]
        nx, ny = x + dx, y + dy
        # clear bit on current cell
        self.grid[y][x].walls &= ~(1 << direction)
        # clear matching bit on neighbour
        self.grid[ny][nx].walls &= ~(1 << OPPOSITE[direction])

    def _carve_passages(self) -> None:
        """Recursive backtracker (iterative DFS) to carve the maze."""
        visited: set[tuple[int, int]] = set()
        stack: list[tuple[int, int]] = [self.entry]
        visited.add(self.entry)

        while stack:
            x, y = stack[-1]
            neighbours = []
            for direction, (dx, dy) in DELTA.items():
                nx, ny = x + dx, y + dy
                if self._in_bounds(nx, ny) and (nx, ny) not in visited:
                    neighbours.append((direction, nx, ny))

            if not neighbours:
                stack.pop()
                continue

            direction, nx, ny = self._rng.choice(neighbours)
            self._open_wall(x, y, direction)
            visited.add((nx, ny))
            stack.append((nx, ny))

        # ensure entry/exit cells have an opening on the border
        self._open_border(self.entry)
        self._open_border(self.exit_)

    def _open_border(self, pos: tuple[int, int]) -> None:
        """Open one external wall on a border cell."""
        x, y = pos
        if y == 0:
            self.grid[y][x].walls &= ~(1 << NORTH)
        elif y == self.height - 1:
            self.grid[y][x].walls &= ~(1 << SOUTH)
        elif x == 0:
            self.grid[y][x].walls &= ~(1 << WEST)
        elif x == self.width - 1:
            self.grid[y][x].walls &= ~(1 << EAST)

    def _add_extra_passages(self) -> None:
        """Add ~15% extra openings to create loops (imperfect maze)."""
        n_extra = max(1, (self.width * self.height) // 7)
        for _ in range(n_extra):
            x = self._rng.randint(0, self.width - 2)
            y = self._rng.randint(0, self.height - 2)
            direction = self._rng.choice([EAST, SOUTH])
            self._open_wall(x, y, direction)

    # ------------------------------------------------------------------
    # "42" pattern
    # ------------------------------------------------------------------

    def _embed_42(self) -> None:
        """Carve a visible '42' glyph using fully-closed cells.

        The glyph is placed in the lower-right quadrant.
        Each digit is drawn on a 3×5 cell grid.
        Raises ValueError if the maze is too small.
        """
        # glyph bitmaps: 1 = closed (wall) cell, 0 = passage cell
        FOUR = [
            [1, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [0, 0, 1],
        ]
        TWO = [
            [1, 1, 1],
            [0, 0, 1],
            [1, 1, 1],
            [1, 0, 0],
            [1, 1, 1],
        ]

        glyph_w = 3 + 1 + 3  # two 3-wide digits + 1-col gap
        glyph_h = 5

        if self.width < glyph_w + 4 or self.height < glyph_h + 4:
            raise ValueError(
                "Maze too small to embed '42' pattern "
                f"(need at least {glyph_w + 4}×{glyph_h + 4})."
            )

        # place in lower-right quadrant with a 2-cell margin
        ox = self.width - glyph_w - 2
        oy = self.height - glyph_h - 2

        def seal_cell(cx: int, cy: int) -> None:
            """Close all four walls of a cell."""
            self.grid[cy][cx].walls = 0b1111
            for direction, (dx, dy) in DELTA.items():
                nx, ny = cx + dx, cy + dy
                if self._in_bounds(nx, ny):
                    self.grid[ny][nx].walls |= (1 << OPPOSITE[direction])

        digits = [FOUR, TWO]
        for digit_idx, bitmap in enumerate(digits):
            dx_offset = digit_idx * 4  # 3 cols + 1 gap
            for row in range(glyph_h):
                for col in range(3):
                    if bitmap[row][col]:
                        seal_cell(ox + dx_offset + col, oy + row)

    # ------------------------------------------------------------------
    # BFS solver
    # ------------------------------------------------------------------

    def _solve(self) -> None:
        """BFS shortest path from entry to exit, stored as direction chars."""
        start = self.entry
        goal = self.exit_
        queue: deque[tuple[tuple[int, int], list[str]]] = deque()
        queue.append((start, []))
        visited: set[tuple[int, int]] = {start}

        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == goal:
                self.solution = path
                return

            for direction, (dx, dy) in DELTA.items():
                nx, ny = x + dx, y + dy
                if (
                    self._in_bounds(nx, ny)
                    and (nx, ny) not in visited
                    and not (self.grid[y][x].walls >> direction & 1)
                ):
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [DIR_CHAR[direction]]))

        self.solution = []  # no path found (shouldn't happen in a perfect maze)

    def wall_closed(self, x: int, y: int, direction: int) -> bool:
        """Return True if the wall in `direction` from cell (x, y) is closed."""
        return bool(self.grid[y][x].walls >> direction & 1)

    def to_hex_grid(self) -> list[list[str]]:
        """Return the grid as hex-char strings (one char per cell)."""
        return [
            [format(self.grid[y][x].walls, 'X') for x in range(self.width)]
            for y in range(self.height)
        ]
    
if __name__ == "__main__":
    # Create maze
    mg = MazeGenerator(
    width=15,
    height=15,
    entry=(0, 0),
    exit_=(14, 14),
    seed=42
)

    # Generate maze
    mg.generate()

    # Print solution path
    print("Solution path:")
    print(" -> ".join(mg.solution))

    # Print grid (hex representation)
    print("\nMaze grid (hex walls):")
    for row in mg.to_hex_grid():
        print(" ".join(row))