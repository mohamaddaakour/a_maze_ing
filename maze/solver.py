from collections import deque
from typing import List, Tuple, Dict, Set

from maze.generator import Maze, Cell


class MazeSolver:
    """
    Solves a maze using BFS to find the shortest path.
    """

    def __init__(self, maze: Maze) -> None:
        self.maze = maze

    def solve(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Find shortest path from start to end using BFS.
        Returns list of coordinates [(x,y), ...]
        """

        queue = deque()
        queue.append(start)

        visited: Set[Tuple[int, int]] = set()
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

        visited.add(start)

        while queue:
            x, y = queue.popleft()

            if (x, y) == end:
                break

            current_cell = self.maze.get_cell(x, y)

            for neighbor, wall, _ in self.maze.get_neighbors(current_cell):
                nx, ny = neighbor.x, neighbor.y

                if (nx, ny) in visited:
                    continue

                # IMPORTANT: check if wall exists
                # If wall bit is set → you cannot pass
                if current_cell.walls & wall:
                    continue

                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)
                queue.append((nx, ny))

        # Reconstruct path
        path: List[Tuple[int, int]] = []
        node = end

        if node not in parent and node != start:
            return []  # no path found (should not happen in valid maze)

        while node != start:
            path.append(node)
            node = parent[node]

        path.append(start)
        path.reverse()

        return path