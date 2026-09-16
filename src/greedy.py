"""Priority-based greedy donation allocation."""

from collections.abc import Iterable

from .fifo import allocate_fifo
from .models import Allocation, Donation, Recipient


def allocate_greedy(donations: Iterable[Donation], recipients: Iterable[Recipient]) -> list[Allocation]:
    ordered = sorted(enumerate(recipients), key=lambda pair: (-pair[1].priority, pair[0]))
    return allocate_fifo(donations, [recipient for _, recipient in ordered])