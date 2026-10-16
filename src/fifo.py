"""First-in, first-out donation allocation."""

from collections.abc import Iterable

from .matching import run_matching
from .models import Allocation, Donation, Recipient, Volunteer


def allocate_fifo(donations: Iterable[Donation], recipients: Iterable[Recipient], volunteers: Iterable[Volunteer]) -> list[Allocation]:
    return run_matching(donations, recipients, volunteers)