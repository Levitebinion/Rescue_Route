"""Domain models used by RescueRoute."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Donation:
    id: str
    item: str
    quantity: int
    donated_at: str = ""
    location: str = ""


@dataclass(frozen=True)
class Recipient:
    id: str
    name: str
    item: str
    quantity: int
    priority: int = 0
    location: str = ""


@dataclass(frozen=True)
class Volunteer:
    id: str
    name: str
    capacity: int = 1
    location: str = ""
    available: bool = True


@dataclass(frozen=True)
class Allocation:
    donation_id: str
    recipient_id: str
    item: str
    quantity: int
    volunteer_id: str | None = None