"""Validation for loaded RescueRoute records."""

from collections.abc import Iterable

from .models import Donation, Recipient, Volunteer


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _require_positive(value: int, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")


def validate_donation(donation: Donation) -> Donation:
    _require_text(donation.id, "donation.id")
    _require_text(donation.item, "donation.item")
    _require_positive(donation.quantity, "donation.quantity")
    return donation


def validate_recipient(recipient: Recipient) -> Recipient:
    _require_text(recipient.id, "recipient.id")
    _require_text(recipient.name, "recipient.name")
    _require_text(recipient.item, "recipient.item")
    _require_positive(recipient.quantity, "recipient.quantity")
    if isinstance(recipient.priority, bool) or not isinstance(recipient.priority, int):
        raise ValueError("recipient.priority must be an integer")
    return recipient


def validate_volunteer(volunteer: Volunteer) -> Volunteer:
    _require_text(volunteer.id, "volunteer.id")
    _require_text(volunteer.name, "volunteer.name")
    _require_positive(volunteer.capacity, "volunteer.capacity")
    if not isinstance(volunteer.available, bool):
        raise ValueError("volunteer.available must be a boolean")
    return volunteer


def validate_unique_ids(records: Iterable[Donation | Recipient | Volunteer]) -> None:
    ids: set[str] = set()
    for record in records:
        if record.id in ids:
            raise ValueError(f"duplicate id: {record.id}")
        ids.add(record.id)