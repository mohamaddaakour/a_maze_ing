from dataclasses import dataclass
from typing import Tuple


# this is a decorator for a class to store data
@dataclass
class Config:
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool


def read_config_file(filepath: str) -> list[str]:
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            # this will create a list and each is an element in it?
            return file.readlines()
    except FileNotFoundError:
        raise ValueError(f"config file not found: {filepath}")


def parse_lines(lines: list[str]) -> dict[str, str]:
    config_dict: dict[str, str] = {}

    for line in lines:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise ValueError(f"Invalid line: {line}")

        key, value = line.split("=", 1)
        config_dict[key.strip()] = value.strip()

    return config_dict


def parse_tuple(value: str) -> tuple[int, int]:
    try:
        x, y = value.split(",")
        return int(x), int(y)
    except Exception:
        raise ValueError(f"Invalid tuple format: {value}")


def parse_bool(value: str) -> bool:
    # Ensured both conditions use .lower()
    if value.lower() == "false":
        return False

    if value.lower() == "true":
        return True

    raise ValueError(f"Invalid boolean: {value}")


def build_config(data: dict[str, str]) -> Config:
    required_keys = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    ]

    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing key: {key}")

    width = int(data["WIDTH"])
    height = int(data["HEIGHT"])
    entry = parse_tuple(data["ENTRY"])
    exit_ = parse_tuple(data["EXIT"])
    output_file = data["OUTPUT_FILE"]
    perfect = parse_bool(data["PERFECT"])

    # validation
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive")

    if entry == exit_:
        raise ValueError("Entry and exit must be different")

    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ValueError("Entry out of bounds")

    if not (0 <= exit_[0] < width and 0 <= exit_[1] < height):
        raise ValueError("Exit out of bounds")

    return Config(width, height, entry, exit_, output_file, perfect)


def parse_config(filepath: str) -> Config:
    lines = read_config_file(filepath)
    data = parse_lines(lines)

    return build_config(data)
