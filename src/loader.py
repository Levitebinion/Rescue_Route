"""Load RescueRoute records from CSV or JSON files."""

import csv
import json
from dataclasses import fields
from pathlib import Path
from typing import Any, TypeVar

from .models import Donation, Recipient, Volunteer
from .validation import (
    validate_donation,
    validate_recipient,
    validate_unique_ids,
    validate_volunteer,
)

Record = TypeVar("Record", Donation, Recipient, Volunteer)

_INT_FIELDS = {
    "quantity", "priority", "capacity", "shelf_life_minutes", "ready_time",
    "closing_time", "vehicle_capacity", "max_pickups",
}


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() not in {"0", "false", "no", "off", ""}


def _as_food_types(value: Any) -> frozenset[str]:
    if isinstance(value, (list, tuple, set, frozenset)):
        return frozenset(str(item).strip() for item in value if str(item).strip())
    return frozenset(item.strip() for item in str(value).split("|") if item.strip())


def _record(model: type[Record], row: dict[str, Any]) -> Record:
    names = {field.name for field in fields(model)}
    values = {key: value for key, value in row.items() if key in names and value != ""}
    for key in _INT_FIELDS & values.keys():
        values[key] = int(values[key])
    if "available" in values:
        values["available"] = _as_bool(values["available"])
    if "accepted_food_types" in values:
        values["accepted_food_types"] = _as_food_types(values["accepted_food_types"])
    return model(**values)


def load_records(path: str | Path, model: type[Record]) -> list[Record]:
    source = Path(path)
    if source.suffix.lower() == ".json":
        rows = json.loads(source.read_text())
    elif source.suffix.lower() == ".csv":
        with source.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
    else:
        raise ValueError("input files must use .csv or .json")
    if not isinstance(rows, list):
        raise ValueError("JSON input must contain a list of records")

    records = [_record(model, row) for row in rows]
    validate_unique_ids(records)

    validator = {Donation: validate_donation, Recipient: validate_recipient, Volunteer: validate_volunteer}[model]
    return [validator(record) for record in records]


def load_donations(path: str | Path) -> list[Donation]:
    return load_records(path, Donation)


def load_recipients(path: str | Path) -> list[Recipient]:
    return load_records(path, Recipient)


def load_volunteers(path: str | Path) -> list[Volunteer]:
    return load_records(path, Volunteer)