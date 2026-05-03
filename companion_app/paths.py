from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    return get_project_root() / "data"


def get_config_path() -> Path:
    return get_data_dir() / "config.json"


def get_assets_dir() -> Path:
    return get_project_root() / "assets"


def get_sprites_dir() -> Path:
    return get_assets_dir() / "sprites" / "cat"
