from companion_app.paths import get_assets_dir, get_sprites_dir


def test_default_sprites_dir_points_to_cat_assets():
    assert get_sprites_dir() == get_assets_dir() / "sprites" / "cat"
