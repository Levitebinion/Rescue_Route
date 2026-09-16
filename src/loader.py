"""Load RescueRoute records from CSV or JSON files."""

import csv
import json
from dataclasses import fields
from pathlib import Path
from typing import Any, TypeVar

from .models import Donation, Recipient, Volunteer
from .validation import validate_donation, validate_recipient, validate_volunteer

Record = TypeVar("Record", Donation, Recipient, Volunteer)


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() not in {"0", "false", "no", "off", ""}


def _record(model: type[Record], row: dict[str, Any]) -> Record:
    names = {field.name for field in fields(model)}
    values = {key: value for key, value in row.items() if key in names and value != ""}
    for key in {"quantity", "priority", "capacity"} & values.keys():
        values[key] = int(values[key])
    if "available" in values:
        values["available"] = _as_bool(values["available"])
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
    validator = {Donation: validate_donation, Recipient: validate_recipient, Volunteer: validate_volunteer}[model]
    return [validator(record) for record in records]


def load_donations(path: str | Path) -> list[Donation]:
    return load_records(path, Donation)


def load_recipients(path: str | Path) -> list[Recipient]:
    return load_records(path, Recipient)


def load_volunteers(path: str | Path) -> list[Volunteer]:
    return load_records(path, Volunteer)