from pathlib import Path
from tools.common import load_config


def test_load_config_reads_yaml(tmp_path):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        "podcast:\n  title: T\ntts:\n  voice: V\n", encoding="utf-8"
    )
    cfg = load_config(str(cfg_file))
    assert cfg["podcast"]["title"] == "T"
    assert cfg["tts"]["voice"] == "V"
