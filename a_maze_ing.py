#!/usr/bin/env python3

import sys
from maze.parser import parse_config
from maze.generator import Maze
from maze.solver import MazeSolver


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    print("Maze Generator started")
    print(f"Using config file: {config_file}")

    config = parse_config(config_file)

    print("Config loaded successfully:")
    print(config)

    maze = Maze(10, 10)
    cell1 = maze.get_cell(0, 0)
    cell2 = maze.get_cell(1, 0)

    maze.remove_wall_between(cell1, cell2)

    print(cell1.walls)
    print(cell2.walls)

    maze.generate()

    solver = MazeSolver(maze)
    path = solver.solve((0, 0), (9, 9))

    print("Path:")
    print(path)
    print("Length:", len(path))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
