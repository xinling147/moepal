import json
import logging
from copy import deepcopy
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_CONFIG: dict[str, Any] = {
    "personality": "gentle",
    "ai_enabled": False,
    "ai_provider": "deepseek",
    "pet_size": 128,
    "bubble_enabled": True,
    "start_on_boot": False,
    "last_position": None,
}

_VALID_PERSONALITIES = frozenset({"gentle", "lively", "quiet"})
_VALID_PET_SIZES = frozenset({128, 160})

# Keys allowed in config file. Anything not in this set is stripped on save.
_KNOWN_KEYS = frozenset(DEFAULT_CONFIG.keys())

# Substrings that mark a key as an API-key-like field.
_API_KEY_SUBSTRINGS = ("api_key", "apikey", "secret", "token")

# Keys that must be strict bool.
_BOOL_KEYS = frozenset({"ai_enabled", "bubble_enabled", "start_on_boot"})


def _looks_like_api_key(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in _API_KEY_SUBSTRINGS)


def _is_valid_position(value: Any) -> bool:
    """Return True if value is None or {"x": int, "y": int}."""
    if value is None:
        return True
    if not isinstance(value, dict) or set(value.keys()) != {"x", "y"}:
        return False
    return all(isinstance(value[key], int) and not isinstance(value[key], bool) for key in ("x", "y"))


def _validate_config_data(data: dict[str, Any], source: Path | str = "config") -> dict[str, Any]:
    config = deepcopy(DEFAULT_CONFIG)

    for key in _KNOWN_KEYS:
        if key not in data:
            continue

        value = data[key]

        if key == "personality":
            if isinstance(value, str) and value in _VALID_PERSONALITIES:
                config[key] = value
            else:
                logger.warning(
                    "Invalid personality '%s' in %s, using default '%s'.",
                    value,
                    source,
                    config[key],
                )
        elif key == "pet_size":
            if isinstance(value, int) and not isinstance(value, bool) and value in _VALID_PET_SIZES:
                config[key] = value
            else:
                logger.warning(
                    "Invalid pet_size '%s' in %s, using default %s.",
                    value,
                    source,
                    config[key],
                )
        elif key in _BOOL_KEYS:
            if isinstance(value, bool):
                config[key] = value
            else:
                logger.warning(
                    "Invalid %s '%s' in %s (expected bool), using default %s.",
                    key,
                    value,
                    source,
                    config[key],
                )
        elif key == "last_position":
            if _is_valid_position(value):
                config[key] = value
            else:
                logger.warning(
                    "Invalid last_position '%s' in %s, using default %s.",
                    value,
                    source,
                    config[key],
                )
        else:
            config[key] = value

    return config


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return deepcopy(DEFAULT_CONFIG)

    try:
        raw = config_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Config file %s is corrupt (%s), using defaults.", config_path, exc)
        return deepcopy(DEFAULT_CONFIG)

    if not isinstance(data, dict):
        logger.warning("Config file %s is not a JSON object, using defaults.", config_path)
        return deepcopy(DEFAULT_CONFIG)

    return _validate_config_data(data, config_path)


def save_config(config: dict[str, Any], config_path: Path) -> None:
    validated = _validate_config_data(config, "save_config input")
    clean: dict[str, Any] = {}
    for key in _KNOWN_KEYS:
        if key in validated and not _looks_like_api_key(key):
            clean[key] = validated[key]

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(clean, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
