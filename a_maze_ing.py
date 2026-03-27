"""A-Maze-ing: generate, display, and save a maze from a config file."""

import sys
from pathlib import Path

from mazegen.generator import MazeGenerator
from maze_renderer import AsciiRenderer, write_output


def parse_config(path: str) -> dict[str, str]:
    """Parse a KEY=VALUE config file, ignoring comment lines.

    Args:
        path: Path to the config file.

    Returns:
        Dictionary of key → value strings.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If a required key is missing or a line is malformed.
    """
    required = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
    config: dict[str, str] = {}

    try:
        with open(path) as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(
                        f"Line {lineno}: expected KEY=VALUE, got: {line!r}"
                    )
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path!r}")

    missing = required - config.keys()
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(sorted(missing))}")

    return config


def build_generator(config: dict[str, str]) -> MazeGenerator:
    """Construct a MazeGenerator from parsed config values.

    Args:
        config: Dictionary from parse_config().

    Returns:
        A configured (but not yet generated) MazeGenerator.

    Raises:
        ValueError: On invalid values (non-integer size, bad coords, etc.).
    """
    try:
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])
    except ValueError:
        raise ValueError("WIDTH and HEIGHT must be integers.")

    if width < 2 or height < 2:
        raise ValueError("WIDTH and HEIGHT must be at least 2.")

    def parse_coord(raw: str, label: str) -> tuple[int, int]:
        parts = raw.split(",")
        if len(parts) != 2:
            raise ValueError(f"{label} must be 'x,y', got: {raw!r}")
        try:
            x, y = int(parts[0]), int(parts[1])
        except ValueError:
            raise ValueError(f"{label} coordinates must be integers.")
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError(
                f"{label} ({x},{y}) is outside the maze bounds "
                f"({width}×{height})."
            )
        return x, y

    entry = parse_coord(config["ENTRY"], "ENTRY")
    exit_ = parse_coord(config["EXIT"], "EXIT")

    if entry == exit_:
        raise ValueError("ENTRY and EXIT must be different cells.")

    perfect = config["PERFECT"].strip().lower() in ("true", "1", "yes")
    seed_raw = config.get("SEED", "").strip()
    seed = int(seed_raw) if seed_raw else None

    return MazeGenerator(
        width=width,
        height=height,
        entry=entry,
        exit_=exit_,
        perfect=perfect,
        seed=seed,
    )


def main() -> None:
    """Entry point: parse args, generate maze, write output, display."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        config = parse_config(config_path)
        mg = build_generator(config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        mg.generate()
    except ValueError as exc:
        # "42" pattern won't fit — non-fatal, maze still generated without it
        print(f"Warning: {exc}", file=sys.stderr)

    output_path = config["OUTPUT_FILE"]
    try:
        write_output(mg, output_path)
    except OSError as exc:
        print(f"Error writing output file: {exc}", file=sys.stderr)
        sys.exit(1)

    renderer = AsciiRenderer(mg)
    renderer.run_interactive()


if __name__ == "__main__":
    main()