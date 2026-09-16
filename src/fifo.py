"""First-in, first-out donation allocation."""

from collections.abc import Iterable

from .models import Allocation, Donation, Recipient


def allocate_fifo(donations: Iterable[Donation], recipients: Iterable[Recipient]) -> list[Allocation]:
    remaining = [[donation, donation.quantity] for donation in donations]
    allocations: list[Allocation] = []
    for recipient in recipients:
        needed = recipient.quantity
        for donation, available in remaining:
            if needed == 0:
                break
            if available == 0 or donation.item != recipient.item:
                continue
            quantity = min(available, needed)
            allocations.append(Allocation(donation.id, recipient.id, donation.item, quantity))
            needed -= quantity
            remaining[remaining.index([donation, available])][1] -= quantity
    return allocations