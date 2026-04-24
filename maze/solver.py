from collections import deque
from typing import List, Tuple, Dict, Set

from maze.generator import Maze, Cell


# here the algorithm to solve the maze
class MazeSolver:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze

    def solve(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        # queue is used for BFS (first in first out)
        queue = deque()
        queue.append(start)

        visited: Set[Tuple[int, int]] = set()
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

        visited.add(start)

        while queue:
            x, y = queue.popleft()

            # if we reach the end cell stop
            if (x, y) == end:
                break

            current_cell = self.maze.get_cell(x, y)

            # scan all neighboors
            for neighbor, wall, _ in self.maze.get_neighbors(current_cell):
                nx, ny = neighbor.x, neighbor.y

                if (nx, ny) in visited:
                    continue

                # if there is a block skip
                if current_cell.walls & wall:
                    continue

                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)
                queue.append((nx, ny))

        path: List[Tuple[int, int]] = []
        node = end

        # if we never reached the goal
        if node not in parent and node != start:
            return []

        while node != start:
            path.append(node)
            node = parent[node]

        path.append(start)
        path.reverse()

        return path