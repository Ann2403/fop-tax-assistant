import csv
import json
from pathlib import Path

import pytest

from fop_tax_assistant.schema import FopRequest

DATA_DIR = Path(__file__).parent.parent / "data"


def load_manifest() -> list[dict[str, str]]:
    with open(DATA_DIR / "manifest.csv", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def golden_ids_from_manifest() -> set[str]:
    return {row["id"] for row in load_manifest() if row["golden"] == "True"}


def test_every_manifest_row_has_a_text():
    for row in load_manifest():
        assert (DATA_DIR / "texts" / f"{row['id']}.txt").is_file(), row["id"]


def test_dataset_meets_the_minimum_size():
    assert len(load_manifest()) >= 30
    assert len(golden_ids_from_manifest()) >= 10


def test_golden_files_match_the_manifest():
    golden_files = {path.stem for path in (DATA_DIR / "golden").glob("*.json")}

    assert golden_files == golden_ids_from_manifest()


@pytest.mark.parametrize("text_id", sorted(golden_ids_from_manifest()))
def test_golden_label_is_valid_against_the_schema(text_id: str):
    label = json.loads((DATA_DIR / "golden" / f"{text_id}.json").read_text(encoding="utf-8"))

    FopRequest.model_validate(label)
