from pathlib import Path

from exchange_changelog.config import Config
from exchange_changelog.config import Document
from exchange_changelog.config import load_config


def test_load_config(tmp_path: Path) -> None:
    yaml_content = """
    docs:
      - name: Test API
        url: http://example.com
    num_days: 7
    trim_len: 10000
    slack_channel: test_channel
    prompt: Test prompt
    """
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content)
    config = load_config(yaml_file)

    assert isinstance(config, Config)
    assert len(config.docs) == 1
    assert config.docs[0].name == "Test API"
    assert config.docs[0].url == "http://example.com"
    assert config.num_days == 7
    assert config.trim_len == 10000
    assert config.slack_channel == "test_channel"
    assert config.prompt == "Test prompt"


def test_config_defaults() -> None:
    config = Config()

    assert config.docs == []
    assert config.num_days == 14
    assert config.trim_len == 20000
    assert config.slack_channel is None
    assert config.prompt == ""


def test_apidoc_model() -> None:
    apidoc = Document(name="Test API", url="http://example.com")

    assert apidoc.name == "Test API"
    assert apidoc.url == "http://example.com"
