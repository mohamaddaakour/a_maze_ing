#!/usr/bin/env python3

import sys
from maze.parser import parse_config


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: pytho3 a_maze_ing.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    print("Maze Generator started")
    print(f"Using config file: {config_file}")

    config = parse_config(config_file)

    print("Config loaded successfully:")
    print(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
