from dataclasses import dataclass
from typing import List
import random

# Directions (bitmask)
NORTH = 1  # 0001
EAST = 2   # 0010
SOUTH = 4  # 0100
WEST = 8   # 1000


@dataclass
class Cell:
    x: int
    y: int
    # 15 in binary is 1111, meaning all walls are closed
    walls: int = 15

    # Check if a specific wall exists
    def has_wall(self, wall: int) -> bool:
        # & is bitwise AND
        return (self.walls & wall) != 0

    # Remove specific wall
    def remove_wall(self, wall: int) -> None:
        # ~ is bitwise NOT
        self.walls &= ~wall


class Maze:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.grid: List[List[Cell]] = [
            [Cell(x, y) for x in range(width)] for y in range(height)
        ]
        self.visited = set()

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> Cell:
        return self.grid[y][x]

    def get_neighbors(self, cell: Cell) -> List[tuple[Cell, int, int]]:
        neighbors = []

        directions = [
            (0, -1, NORTH, SOUTH),  # North
            (1, 0, EAST, WEST),     # East
            (0, 1, SOUTH, NORTH),   # South
            (-1, 0, WEST, EAST),    # West
        ]

        for dx, dy, wall, opposite in directions:
            nx, ny = cell.x + dx, cell.y + dy

            if self.in_bounds(nx, ny):
                neighbor = self.get_cell(nx, ny)
                neighbors.append((neighbor, wall, opposite))

        return neighbors

    def remove_wall_between(self, current: Cell, neighbor: Cell) -> None:
        dx = neighbor.x - current.x
        dy = neighbor.y - current.y

        if dx == 1:
            current.remove_wall(EAST)
            neighbor.remove_wall(WEST)
        elif dx == -1:
            current.remove_wall(WEST)
            neighbor.remove_wall(EAST)
        elif dy == 1:
            current.remove_wall(SOUTH)
            neighbor.remove_wall(NORTH)
        elif dy == -1:
            current.remove_wall(NORTH)
            neighbor.remove_wall(SOUTH)

    
    def get_unvisited_neighbors(self, cell: Cell):
        neighbors = []

        for neighbor, wall, opposite in self.get_neighbors(cell):
            if (neighbor.x, neighbor.y) not in self.visited:
                neighbors.append((neighbor, wall, opposite))

        return neighbors
    
    def generate(self, start_x: int = 0, start_y: int = 0) -> None:
        stack = []

        start = self.get_cell(start_x, start_y)
        stack.append(start)
        self.visited.add((start.x, start.y))

        while stack:
            current = stack[-1]

            neighbors = self.get_unvisited_neighbors(current)

            if neighbors:
                neighbor, wall, opposite = random.choice(neighbors)

                # Remove wall between current and neighbor
                self.remove_wall_between(current, neighbor)

                # Mark visited
                self.visited.add((neighbor.x, neighbor.y))

                # Go deeper
                stack.append(neighbor)
            else:
                # Backtrack
                stack.pop()