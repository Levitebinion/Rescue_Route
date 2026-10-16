"""Urgency-first greedy donation allocation.

Greedy rule (document this exact wording in the README too):
  1. Schedule donations with the LEAST remaining shelf life first.
  2. If two donations have equal remaining shelf life, schedule the
     LARGER quantity first.
  3. If still tied, use the earlier ready_time.
  4. If still tied, keep arrival order.

Any donation that ends up being processed after a donation that arrived
later than it is "deferred", and its explanation says which donations went
ahead of it and why.
"""

from collections.abc import Iterable

from .matching import Deferrals, run_matching
from .models import Allocation, Donation, Recipient, Volunteer


def _urgency_key(donation: Donation) -> tuple[int, int, int]:
    return (donation.shelf_life_minutes, -donation.quantity, donation.ready_time)


def _why_ahead(ahead: Donation, behind: Donation) -> str:
    """Short reason the `ahead` donation outranks the `behind` one."""
    if ahead.shelf_life_minutes < behind.shelf_life_minutes:
        return "less remaining shelf life"
    if ahead.quantity > behind.quantity:
        return "equal shelf life but a larger quantity"
    return "equal shelf life and quantity but an earlier ready time"


def _find_deferrals(ordered: list[tuple[int, Donation]]) -> Deferrals:
    """`ordered` is (arrival_index, donation) in processing order."""
    deferrals: Deferrals = {}
    for position, (arrival_index, donation) in enumerate(ordered):
        jumpers = tuple(
            (other.id, _why_ahead(other, donation))
            for other_index, other in ordered[:position]
            if other_index > arrival_index
        )
        if jumpers:
            deferrals[donation.id] = jumpers
    return deferrals


def allocate_greedy(donations: Iterable[Donation], recipients: Iterable[Recipient],
                     volunteers: Iterable[Volunteer]) -> list[Allocation]:
    # sorted() is stable, so full ties keep arrival order.
    ordered = sorted(enumerate(donations), key=lambda pair: _urgency_key(pair[1]))
    processing_order = [donation for _, donation in ordered]
    return run_matching(processing_order, recipients, volunteers, _find_deferrals(ordered))
    return run_matching(ordered_donations, recipients, volunteers)
