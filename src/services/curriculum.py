import json
from pathlib import Path


class CurriculumLoader:
    def __init__(self, path: Path | None = None):
        if path is None:
            path = Path(__file__).parent.parent / "data" / "curriculum.json"
        with open(path) as f:
            self._data = json.load(f)
        self._units_by_id = {u["id"]: u for u in self._data["units"]}

    def get_units(self) -> list[dict]:
        return sorted(self._data["units"], key=lambda u: u["order"])

    def get_vocab(self, unit_id: str) -> list[dict]:
        if unit_id not in self._units_by_id:
            raise KeyError(f"Unknown unit: {unit_id}")
        return self._units_by_id[unit_id]["vocab"]

    def get_sentences(self, unit_id: str) -> list[dict]:
        if unit_id not in self._units_by_id:
            raise KeyError(f"Unknown unit: {unit_id}")
        return self._units_by_id[unit_id]["sentences"]

    def get_all_slovenian_texts(self) -> list[str]:
        texts = set()
        for unit in self._data["units"]:
            for item in unit["vocab"]:
                texts.add(item["sl"])
                texts.add(item["example"])
            for sent in unit["sentences"]:
                texts.add(sent["sl"])
        return sorted(texts)
