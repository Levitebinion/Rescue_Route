"""Domain models used by RescueRoute."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Donation:
    id: str
    donor_name: str
    food_type: str
    shelf_life_minutes: int
    quantity: int
    pickup_area: str = ""
    ready_time: int = 0


@dataclass(frozen=True)
class Recipient:
    id: str
    name: str
    accepted_food_types: frozenset[str]
    capacity: int
    area: str
    closing_time: int
    priority: int = 0


@dataclass(frozen=True)
class Volunteer:
    id: str
    name: str
    vehicle_capacity: int
    area: str
    available: bool = True
    max_pickups: int = 1


@dataclass(frozen=True)
class Allocation:
    donation_id: str
    recipient_id: str | None
    volunteer_id: str | None
    quantity: int
    decision_reason: str
    status: str
    deferred_after: tuple[str, ...] = ()