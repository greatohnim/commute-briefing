import yaml


def load_config(path):
    """YAML 설정 파일을 dict로 로드한다."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
