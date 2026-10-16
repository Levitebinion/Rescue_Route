"""Priority-based greedy donation allocation."""

from collections.abc import Iterable

from .matching import run_matching
from .models import Allocation, Donation, Recipient, Volunteer


def _urgency_key(donation: Donation) -> tuple[int, int, int]:
    return (donation.shelf_life_minutes, -donation.quantity, donation.ready_time)


def allocate_greedy(donations: Iterable[Donation], recipients: Iterable[Recipient], volunteers: Iterable[Volunteer]) -> list[Allocation]:
    ordered_donations = sorted(donations, key=_urgency_key)
    return run_matching(ordered_donations, recipients, volunteers)
