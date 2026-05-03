import json

import pytest

from companion_app.config import DEFAULT_CONFIG, load_config, save_config


# ---- helpers ---------------------------------------------------------------

def _cfg_path(tmp_path, filename="config.json"):
    return tmp_path / filename


# ---- TC-1: 配置文件不存在时返回默认配置 -------------------------------------

def test_load_config_returns_defaults_when_file_missing(tmp_path):
    config = load_config(_cfg_path(tmp_path))

    assert config["personality"] == "gentle"
    assert config["ai_enabled"] is False
    assert config["ai_provider"] == "deepseek"
    assert config["pet_size"] == 128
    assert config["bubble_enabled"] is True
    assert config["start_on_boot"] is False
    assert config["last_position"] is None


# ---- TC-2: 配置文件损坏时回退默认配置 ----------------------------------------

def test_load_config_falls_back_to_defaults_on_corrupted_json(tmp_path, caplog):
    path = _cfg_path(tmp_path)
    path.write_text("{not valid json", encoding="utf-8")

    config = load_config(path)

    assert config["personality"] == "gentle"
    assert config["ai_enabled"] is False

    assert any("corrupt" in r.message.lower() or "using defaults" in r.message.lower()
               for r in caplog.records)


def test_load_config_falls_back_to_defaults_when_not_a_dict(tmp_path, caplog):
    path = _cfg_path(tmp_path)
    path.write_text("[1, 2, 3]", encoding="utf-8")

    config = load_config(path)

    assert config["personality"] == "gentle"
    assert any("not a json object" in r.message.lower() or "defaults" in r.message.lower()
               for r in caplog.records)


# ---- TC-3: 保存配置后能读取 -------------------------------------------------

def test_save_and_load_config_roundtrip(tmp_path):
    path = _cfg_path(tmp_path)
    original = {
        "personality": "lively",
        "ai_enabled": True,
        "ai_provider": "deepseek",
        "pet_size": 160,
        "bubble_enabled": False,
        "start_on_boot": True,
        "last_position": {"x": 100, "y": 200},
    }

    save_config(original, path)
    loaded = load_config(path)

    assert loaded["personality"] == "lively"
    assert loaded["ai_enabled"] is True
    assert loaded["pet_size"] == 160
    assert loaded["bubble_enabled"] is False
    assert loaded["start_on_boot"] is True
    assert loaded["last_position"] == {"x": 100, "y": 200}


# ---- TC-4: API Key 不会写入配置 ----------------------------------------------

def test_save_config_strips_api_key(tmp_path):
    path = _cfg_path(tmp_path)
    save_config(
        {
            "personality": "quiet",
            "ai_enabled": True,
            "deepseek_api_key": "sk-secret",
        },
        path,
    )

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["personality"] == "quiet"
    assert saved["ai_enabled"] is True
    assert "deepseek_api_key" not in saved


def test_save_config_strips_apikey_variants(tmp_path):
    path = _cfg_path(tmp_path)
    save_config(
        {
            "personality": "gentle",
            "deepseek_api_key": "x",
            "openai_apikey": "y",
            "some_secret": "z",
            "auth_token": "t",
        },
        path,
    )

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert "deepseek_api_key" not in saved
    assert "openai_apikey" not in saved
    assert "some_secret" not in saved
    assert "auth_token" not in saved
    assert saved["personality"] == "gentle"


# ---- TC-5: 未知字段保存时被过滤 ---------------------------------------------

def test_save_config_ignores_unknown_fields(tmp_path):
    path = _cfg_path(tmp_path)
    save_config(
        {
            "personality": "lively",
            "unknown_field": "should not appear",
            "another_random": 42,
        },
        path,
    )

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert "unknown_field" not in saved
    assert "another_random" not in saved
    assert saved["personality"] == "lively"


# ---- TC-6: 部分字段缺失时填充默认值 ------------------------------------------

def test_load_config_fills_missing_fields_with_defaults(tmp_path):
    path = _cfg_path(tmp_path)
    path.write_text('{"personality": "quiet"}', encoding="utf-8")

    config = load_config(path)

    assert config["personality"] == "quiet"
    assert config["ai_enabled"] is False
    assert config["pet_size"] == 128
    assert config["bubble_enabled"] is True


# ---- TC-7: personality 只接受有效值 -----------------------------------------

def test_load_config_rejects_invalid_personality(tmp_path, caplog):
    path = _cfg_path(tmp_path)
    path.write_text('{"personality": "angry"}', encoding="utf-8")

    config = load_config(path)

    assert config["personality"] == "gentle"
    assert any("invalid" in r.message.lower() and "personality" in r.message.lower()
               for r in caplog.records)


def test_load_config_accepts_valid_personalities(tmp_path):
    for valid in ("gentle", "lively", "quiet"):
        path = _cfg_path(tmp_path)
        path.write_text(f'{{"personality": "{valid}"}}', encoding="utf-8")
        config = load_config(path)
        assert config["personality"] == valid


# ---- 默认配置完整性 ----------------------------------------------------------

def test_default_config_has_all_expected_keys():
    expected = {"personality", "ai_enabled", "ai_provider", "pet_size",
                "bubble_enabled", "start_on_boot", "last_position"}
    assert set(DEFAULT_CONFIG.keys()) == expected


# ---- TC-25: pet_size 非法值回退默认 ----------------------------------------

@pytest.mark.parametrize("bad_value", [0, -5, 1, 127, 129, 999, "large", 1.5, True, False, [], {}])
def test_load_config_rejects_invalid_pet_size(tmp_path, caplog, bad_value):
    path = _cfg_path(tmp_path)
    path.write_text(json.dumps({"pet_size": bad_value}), encoding="utf-8")
    config = load_config(path)
    assert config["pet_size"] == 128
    assert any("pet_size" in r.message.lower() for r in caplog.records)


# ---- TC-26: bool 字段非法值回退默认 -----------------------------------------

@pytest.mark.parametrize("field", ["ai_enabled", "bubble_enabled", "start_on_boot"])
@pytest.mark.parametrize("bad_value", [1, 0, "yes", None, [], 42])
def test_load_config_rejects_non_bool_for_bool_fields(tmp_path, caplog, field, bad_value):
    path = _cfg_path(tmp_path)
    path.write_text(json.dumps({field: bad_value}), encoding="utf-8")
    config = load_config(path)
    assert config[field] is DEFAULT_CONFIG[field]
    assert any(field in r.message.lower() for r in caplog.records)


# ---- TC-31: last_position 非法值回退默认 ------------------------------------

@pytest.mark.parametrize("bad_value", [
    [1], [1, 2], [1, 2, 3], "0,0", {"x": 1}, {"y": 2},
    {"x": 1, "y": 2, "z": 3}, {"x": True, "y": 1}, {"x": 1, "y": "two"},
    True, [True, 1], [1, "two"],
])
def test_load_config_rejects_invalid_last_position(tmp_path, caplog, bad_value):
    path = _cfg_path(tmp_path)
    path.write_text(json.dumps({"last_position": bad_value}), encoding="utf-8")
    config = load_config(path)
    assert config["last_position"] is None
    assert any("last_position" in r.message.lower() for r in caplog.records)


def test_load_config_accepts_valid_last_position(tmp_path):
    path = _cfg_path(tmp_path)
    path.write_text(json.dumps({"last_position": {"x": 320, "y": 480}}), encoding="utf-8")
    config = load_config(path)
    assert config["last_position"] == {"x": 320, "y": 480}


def test_load_config_accepts_none_last_position(tmp_path):
    path = _cfg_path(tmp_path)
    path.write_text(json.dumps({"last_position": None}), encoding="utf-8")
    config = load_config(path)
    assert config["last_position"] is None


def test_save_config_sanitizes_invalid_known_fields(tmp_path):
    path = _cfg_path(tmp_path)
    save_config(
        {
            "personality": "gentle",
            "ai_enabled": "yes",
            "pet_size": 999,
            "last_position": [10, 20],
        },
        path,
    )

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["ai_enabled"] is False
    assert saved["pet_size"] == 128
    assert saved["last_position"] is None
