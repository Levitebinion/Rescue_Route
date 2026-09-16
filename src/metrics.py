"""Metrics for allocation results."""

from collections.abc import Iterable

from .models import Allocation, Recipient


def total_allocated(allocations: Iterable[Allocation]) -> int:
    return sum(allocation.quantity for allocation in allocations)


def fulfillment_rate(allocations: Iterable[Allocation], recipients: Iterable[Recipient]) -> float:
    requested = sum(recipient.quantity for recipient in recipients)
    return total_allocated(allocations) / requested if requested else 1.0


def allocation_summary(allocations: Iterable[Allocation], recipients: Iterable[Recipient]) -> dict[str, float | int]:
    allocation_list = list(allocations)
    recipient_list = list(recipients)
    return {
        "allocated": total_allocated(allocation_list),
        "requested": sum(recipient.quantity for recipient in recipient_list),
        "fulfillment_rate": fulfillment_rate(allocation_list, recipient_list),
        "allocation_count": len(allocation_list),
    }