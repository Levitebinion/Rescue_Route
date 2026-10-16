"""Shared matching engine.

FIFO and greedy are the *same* matching procedure -- feasibility checks,
one donation -> at most one recipient + one volunteer, with an explanation
for every outcome -- run over donations in a different order. Ordering is
the only thing that should differ between the two strategies, so it lives
here once instead of being duplicated in fifo.py and greedy.py.
"""

from collections.abc import Iterable

from .models import Allocation, Donation, Recipient, Volunteer


def _find_feasible_recipient(donation: Donation, recipients: list[Recipient],
                              remaining_capacity: dict[str, int]) -> Recipient | None:
    for recipient in recipients:
        if donation.food_type not in recipient.accepted_food_types:
            continue
        if remaining_capacity[recipient.id] < donation.quantity:
            continue
        if donation.ready_time > recipient.closing_time:
            continue
        if recipient.area != donation.pickup_area:
            continue
        return recipient
    return None


def _find_feasible_volunteer(donation: Donation, area: str, volunteers: list[Volunteer],
                              pickups_used: dict[str, int]) -> Volunteer | None:
    for volunteer in volunteers:
        if not volunteer.available:
            continue
        if volunteer.area != area:
            continue
        if volunteer.vehicle_capacity < donation.quantity:
            continue
        if pickups_used[volunteer.id] >= volunteer.max_pickups:
            continue
        return volunteer
    return None


def run_matching(donations: Iterable[Donation], recipients: Iterable[Recipient],
                  volunteers: Iterable[Volunteer]) -> list[Allocation]:
    """Process donations in the order given, assigning each to at most one
    feasible recipient + volunteer. Caller controls the order: pass
    donations as-is for FIFO, or pre-sorted by urgency for greedy."""
    recipients = list(recipients)
    volunteers = list(volunteers)
    remaining_capacity = {r.id: r.capacity for r in recipients}
    pickups_used = {v.id: 0 for v in volunteers}

    allocations: list[Allocation] = []
    for donation in donations:
        if donation.shelf_life_minutes <= 0:
            allocations.append(Allocation(
                donation_id=donation.id, recipient_id=None, volunteer_id=None,
                quantity=0, status="unassigned",
                decision_reason=(
                    f"Donation {donation.id} could not be assigned because it had "
                    f"already expired (0 minutes remaining) when processed."
                ),
            ))
            continue

        recipient = _find_feasible_recipient(donation, recipients, remaining_capacity)
        if recipient is None:
            allocations.append(Allocation(
                donation_id=donation.id, recipient_id=None, volunteer_id=None,
                quantity=0, status="unassigned",
                decision_reason=(
                    f"Donation {donation.id} could not be assigned because no "
                    f"recipient accepts '{donation.food_type}' with enough remaining "
                    f"capacity in area '{donation.pickup_area}' before closing time."
                ),
            ))
            continue

        volunteer = _find_feasible_volunteer(donation, recipient.area, volunteers, pickups_used)
        if volunteer is None:
            allocations.append(Allocation(
                donation_id=donation.id, recipient_id=None, volunteer_id=None,
                quantity=0, status="unassigned",
                decision_reason=(
                    f"Donation {donation.id} could not be assigned because no "
                    f"available volunteer in area '{recipient.area}' had enough "
                    f"vehicle capacity or remaining pickups."
                ),
            ))
            continue

        remaining_capacity[recipient.id] -= donation.quantity
        pickups_used[volunteer.id] += 1
        allocations.append(Allocation(
            donation_id=donation.id, recipient_id=recipient.id, volunteer_id=volunteer.id,
            quantity=donation.quantity, status="assigned",
            decision_reason=(
                f"Donation {donation.id} was assigned to {recipient.name} with "
                f"volunteer {volunteer.id} because it had {donation.shelf_life_minutes} "
                f"minutes of shelf life remaining, the recipient accepts "
                f"'{donation.food_type}' with available capacity, and the volunteer "
                f"could carry the quantity ({donation.quantity})."
            ),
        ))

    return allocations