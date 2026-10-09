"""config_parser.py: read and validate the maze configuration file."""


from dataclasses import dataclass
from typing import Final


REQUIRED_KEYS: Final = frozenset(
    {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
)
ALLOWED_KEYS: Final = REQUIRED_KEYS | {"SEED"}
TRUE_VALUES: Final = frozenset({"true", "yes", "1"})
FALSE_VALUES: Final = frozenset({"false", "no", "0"})


class ConfigError(Exception):
    """Raised when the configuration file is missing or malformed."""


@dataclass
class MazeConfig:
    """Typed values read from the configuration file.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell as (x, y).
        exit_: Exit cell as (x, y).
        output_file: Path of the file where the maze is written.
        perfect: Whether the maze has a single path between cells.
        seed: Random seed, or None if the file does not set one.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None


def read_config(path: str) -> dict[str, str]:
    """Read the configuration file into a dictionary of raw strings.

    Empty lines and lines starting with '#' are ignored.

    Args:
        path: Path of the configuration file.

    Returns:
        Dictionary mapping each key to its raw value.

    Raises:
        ConfigError: If the file cannot be read, a line has no '=', or a key
            is empty, duplicated, unknown or missing.
    """
    config: dict[str, str] = {}

    try:
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, sep, value = line.partition("=")
                key = key.strip()
                if not sep:
                    raise ConfigError(f"Invalid line in config file: {line}")
                if not key:
                    raise ConfigError(f"Empty key in config file: {line}")
                if key in config:
                    raise ConfigError(f"Duplicate key in config file: {key}")
                if key not in ALLOWED_KEYS:
                    raise ConfigError(f"Unknown key in config file: {key}")
                config[key] = value.strip()
    except (OSError, UnicodeDecodeError) as error:
        raise ConfigError(f"Error reading config file: {error}") from error

    for key in sorted(REQUIRED_KEYS):
        if key not in config:
            raise ConfigError(f"Missing required key in config file: {key}")

    return config


def parse_int(key: str, value: str) -> int:
    """Convert a raw value into an integer.

    Args:
        key: Name of the key, used in the error message.
        value: Raw value from the file.

    Returns:
        The value as an integer.

    Raises:
        ConfigError: If the value is not an integer.
    """
    try:
        return int(value)
    except ValueError as error:
        raise ConfigError(f"{key}: {value} is not an integer") from error


def parse_coords(key: str, value: str) -> tuple[int, int]:
    """Convert an 'x,y' value into a pair of integers.

    Args:
        key: Name of the key, used in the error message.
        value: Raw value from the file.

    Returns:
        The cell as (x, y).

    Raises:
        ConfigError: If the value does not have exactly two integers.
    """
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key}: expected 'x,y', got '{value}'")
    x = parse_int(key, parts[0].strip())
    y = parse_int(key, parts[1].strip())
    return (x, y)


def parse_bool(key: str, value: str) -> bool:
    """Convert a true/false word or 1/0, in any case, into a boolean.

    Accepted values are true, yes and 1 for True, and false, no and 0 for
    False.

    Args:
        key: Name of the key, used in the error message.
        value: Raw value from the file.

    Returns:
        The value as a boolean.

    Raises:
        ConfigError: If the value is not one of the accepted words.
    """
    lowered = value.strip().lower()
    if lowered in TRUE_VALUES:
        return True
    if lowered in FALSE_VALUES:
        return False
    raise ConfigError(
        f"{key}: expected true/false, yes/no or 1/0, got '{value}'"
    )


def cast_config(config: dict[str, str]) -> MazeConfig:
    """Convert the raw dictionary into a typed MazeConfig.

    Only the format is checked here. Value rules such as a positive size or
    an entry inside the maze are checked by MazeGenerator.

    Args:
        config: Dictionary returned by read_config.

    Returns:
        The typed configuration.

    Raises:
        ConfigError: If a value has the wrong format or OUTPUT_FILE is empty.
    """
    width = parse_int("WIDTH", config["WIDTH"])
    height = parse_int("HEIGHT", config["HEIGHT"])
    entry = parse_coords("ENTRY", config["ENTRY"])
    exit_ = parse_coords("EXIT", config["EXIT"])
    perfect = parse_bool("PERFECT", config["PERFECT"])
    output_file = config["OUTPUT_FILE"]
    seed = parse_int("SEED", config["SEED"]) if "SEED" in config else None

    if not output_file:
        raise ConfigError("OUTPUT_FILE cannot be empty")

    return MazeConfig(
        width,
        height,
        entry,
        exit_,
        output_file,
        perfect,
        seed,
    )


def parse_config(path: str) -> MazeConfig:
    """Read and convert the configuration file.

    Args:
        path: Path of the configuration file.

    Returns:
        The typed configuration.

    Raises:
        ConfigError: If the file cannot be read or is malformed.
    """
    return cast_config(read_config(path))
