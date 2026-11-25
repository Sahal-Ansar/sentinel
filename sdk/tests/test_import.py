import importlib


def test_sdk_imports() -> None:
    module = importlib.import_module("sentinel_obs")
    assert module.__name__ == "sentinel_obs"
