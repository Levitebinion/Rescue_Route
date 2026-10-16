"""Validation for loaded RescueRoute records."""

from collections.abc import Iterable

from .models import Donation, Recipient, Volunteer


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _require_positive(value: int, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")

def _require_nonnegative(value: int, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")


def validate_donation(donation: Donation) -> Donation:
    _require_text(donation.id, "donation.id")
    _require_text(donation.donor_name, "donation.donor_name")
    _require_text(donation.food_type, "donation.food_type")
    _require_positive(donation.quantity, "donation.quantity")
    _require_nonnegative(donation.shelf_life_minutes, "donation.shelf_life_minutes")
    _require_text(donation.pickup_area, "donation.pickup_area")
    _require_nonnegative(donation.ready_time, "donation.ready_time")
    return donation


def validate_recipient(recipient: Recipient) -> Recipient:
    _require_text(recipient.id, "recipient.id")
    _require_text(recipient.name, "recipient.name")
    if not recipient.accepted_food_types:
        raise ValueError("recipient.accepted_food_types must not be empty")
    _require_positive(recipient.capacity, "recipient.capacity")
    _require_text(recipient.area, "recipient.area")
    _require_nonnegative(recipient.closing_time, "recipient.closing_time")
    if isinstance(recipient.priority, bool) or not isinstance(recipient.priority, int):
        raise ValueError("recipient.priority must be an integer")
    return recipient


def validate_volunteer(volunteer: Volunteer) -> Volunteer:
    _require_text(volunteer.id, "volunteer.id")
    _require_text(volunteer.name, "volunteer.name")
    _require_positive(volunteer.vehicle_capacity, "volunteer.vehicle_capacity")
    _require_text(volunteer.area, "volunteer.area")
    if not isinstance(volunteer.available, bool):
        raise ValueError("volunteer.available must be a boolean")
    _require_positive(volunteer.max_pickups, "volunteer.max_pickups")
    return volunteer


def validate_unique_ids(records: Iterable[Donation | Recipient | Volunteer]) -> None:
    ids: set[str] = set()
    for record in records:
        if record.id in ids:
            raise ValueError(f"duplicate id: {record.id}")
        ids.add(record.id)