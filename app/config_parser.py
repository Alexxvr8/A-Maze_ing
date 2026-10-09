"""config_parser.py: read and validate the maze configuration file."""


from dataclasses import dataclass
import sys


REQUIRED_KEYS = {
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
}
ALLOWED_KEYS = REQUIRED_KEYS | {"SEED"}


class ConfigError(Exception):
    """Exception raised for errors in the configuration file."""


@dataclass
class MazeConfig:
    """Class to hold the maze configuration."""
    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None


def get_path() -> str:
    """Get the path to the configuration file from"""
    """the command line arguments."""
    if len(sys.argv) != 2:
        raise ConfigError("Usage: python a_maze_ing.py <config_file>")
    return sys.argv[1]


def read_config(path: str) -> dict[str, str]:
    """Parse the configuration file and return a dict."""
    config: dict[str, str] = {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, sep, value = line.partition("=")
                if not sep:
                    raise ConfigError(f"Invalid line in config file: {line}")
                if key.strip() in config:
                    raise ConfigError(
                        f"Duplicate key in config file: {key.strip()}"
                    )
                if key.strip() not in ALLOWED_KEYS:
                    raise ConfigError(
                        f"Unknown key in config file: {key.strip()}"
                    )
                config[key.strip()] = value.strip()
    except (OSError, UnicodeDecodeError) as e:
        raise ConfigError(f"Error reading config file: {e}")

    for key in REQUIRED_KEYS:
        if key not in config:
            raise ConfigError(f"Missing required key in config file: {key}")

    return config


def parse_int(key: str, value: str) -> int:
    """Convert value to int, raising an error if it fails."""
    try:
        return int(value)
    except ValueError as e:
        raise ConfigError(f"{key}: {value} is not an integer") from e


def parse_coords(key: str, value: str) -> tuple[int, int]:
    """Convert 'x, y' into a tuple of two ints."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key}: expected 'x,y' got '{value}'")
    x = parse_int(key, parts[0].strip())
    y = parse_int(key, parts[1].strip())
    return (x, y)


def parse_bool(key: str, value: str) -> bool:
    """Convert 'True'/'False' (any case) into a bool."""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "yes":
        return True
    if lowered == "no":
        return False
    if lowered == "1":
            return True
    if lowered == "0":
        return False
    raise ConfigError(f"{key}: expected True or False, got '{value}'")


def cast_config(config: dict[str, str]) -> MazeConfig:
    """Cast the config dictionary into a MazeConfig object."""

    width = parse_int("WIDTH", config["WIDTH"])
    height = parse_int("HEIGHT", config["HEIGHT"])
    entry = parse_coords("ENTRY", config["ENTRY"])
    exit_ = parse_coords("EXIT", config["EXIT"])
    perfect = parse_bool("PERFECT", config["PERFECT"])
    output_file = config["OUTPUT_FILE"]
    seed = parse_int("SEED", config["SEED"]) if "SEED" in config else None

    if width <= 0 or height <= 0:
        raise ConfigError("WIDTH and HEIGHT must be positive")
    for name, (x, y) in (("ENTRY", entry), ("EXIT", exit_)):
        if not (0 <= x < width and 0 <= y < height):
            raise ConfigError(f"{name} {x},{y} is outside the maze")
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different.")
    if not output_file:
        raise ConfigError("OUTPUT_FILE cannot be empty")

    return MazeConfig(
        width,
        height,
        entry,
        exit_,
        output_file,
        perfect,
        seed
    )
