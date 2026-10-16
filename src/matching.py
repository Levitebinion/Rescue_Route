"""Shared matching engine.

FIFO and greedy are the *same* matching procedure -- feasibility checks,
one donation -> at most one recipient + one volunteer, with an explanation
for every outcome -- run over donations in a different order. Ordering is
the only thing that should differ between the two strategies, so it lives
here once instead of being duplicated in fifo.py and greedy.py.

Time model: shelf_life_minutes is the shelf life remaining at simulation
start (minute 0). A donation that is not ready for pickup until
ready_time >= shelf_life_minutes has already expired by the time it could
be collected, so it is treated as expired.

Area model: a donation, its recipient and its volunteer must all be in the
same area. That means donations in different areas can never compete for
the same recipient capacity or volunteer pickups.
"""

from collections.abc import Iterable

from .models import Allocation, Donation, Recipient, Volunteer

# deferrals maps donation id -> ((other_id, short_reason), ...): the donations
# that were processed ahead of it even though they arrived later.
Deferrals = dict[str, tuple[tuple[str, str], ...]]

_MAX_LISTED_IN_NOTE = 3


def _compatible_recipients(donation: Donation, recipients: list[Recipient]) -> list[Recipient]:
    """Recipients that could take this donation if they had room: right food
    type, right area, and still open when the donation is ready."""
    return [
        r for r in recipients
        if donation.food_type in r.accepted_food_types
        and r.area == donation.pickup_area
        and donation.ready_time <= r.closing_time
    ]


def _find_feasible_recipient(donation: Donation, recipients: list[Recipient],
                              remaining_capacity: dict[str, int]) -> Recipient | None:
    for recipient in _compatible_recipients(donation, recipients):
        if remaining_capacity[recipient.id] >= donation.quantity:
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


def _expiry_problem(donation: Donation) -> str | None:
    """Return a sentence fragment if the donation can't be rescued in time."""
    if donation.shelf_life_minutes <= 0:
        return "it had already expired (0 minutes remaining) when processed"
    if donation.ready_time >= donation.shelf_life_minutes:
        return (
            f"it would expire after {donation.shelf_life_minutes} minutes, but it is "
            f"not ready for pickup until minute {donation.ready_time}"
        )
    return None


def _join(parts: list[str]) -> str:
    if len(parts) <= 2:
        return " and ".join(parts)
    return ", ".join(parts[:-1]) + ", and " + parts[-1]


def _deferral_note(donation: Donation, deferrals: Deferrals, status_by_id: dict[str, str],
                   area_by_id: dict[str, str]) -> str:
    """Name the donations processed ahead of this one (despite arriving
    later) that were assigned and are in the same area -- only those could
    have taken the recipient capacity or volunteer pickups this donation
    needed."""
    ahead = [
        (other, why) for other, why in deferrals.get(donation.id, ())
        if status_by_id.get(other) == "assigned" and area_by_id[other] == donation.pickup_area
    ]
    if not ahead:
        return ""
    parts = [f"{other} ({why})" for other, why in ahead[:_MAX_LISTED_IN_NOTE]]
    extra = len(ahead) - _MAX_LISTED_IN_NOTE
    if extra > 0:
        parts.append(f"{extra} more")
    verb = "was" if len(ahead) == 1 else "were"
    return (
        f" Under the urgency-first rule it was considered after {_join(parts)}, "
        f"which {verb} assigned first even though this donation arrived earlier."
    )


def run_matching(donations: Iterable[Donation], recipients: Iterable[Recipient],
                  volunteers: Iterable[Volunteer],
                  deferrals: Deferrals | None = None) -> list[Allocation]:
    """Process donations in the order given, assigning each to at most one
    feasible recipient + volunteer. Caller controls the order: pass
    donations as-is for FIFO, or pre-sorted by urgency for greedy (with the
    matching `deferrals` so skipped-ahead donations get an explanation)."""
    donations = list(donations)
    recipients = list(recipients)
    volunteers = list(volunteers)
    deferrals = deferrals or {}
    remaining_capacity = {r.id: r.capacity for r in recipients}
    pickups_used = {v.id: 0 for v in volunteers}
    area_by_id = {d.id: d.pickup_area for d in donations}

    allocations: list[Allocation] = []
    status_by_id: dict[str, str] = {}

    def record(donation: Donation, status: str, reason: str,
               recipient_id: str | None = None, volunteer_id: str | None = None,
               quantity: int = 0, order_matters: bool = True) -> None:
        # order_matters=False for failures processing order can't explain
        # (expired, nobody accepts that food) -- no deferral sentence there.
        note = _deferral_note(donation, deferrals, status_by_id, area_by_id) if order_matters else ""
        allocations.append(Allocation(
            donation_id=donation.id, recipient_id=recipient_id, volunteer_id=volunteer_id,
            quantity=quantity, status=status, decision_reason=reason + note,
            deferred_after=tuple(other for other, _ in deferrals.get(donation.id, ())),
        ))
        status_by_id[donation.id] = status

    for donation in donations:
        problem = _expiry_problem(donation)
        if problem:
            record(donation, "unassigned",
                   f"Donation {donation.id} could not be assigned because {problem}.",
                   order_matters=False)
            continue

        compatible = _compatible_recipients(donation, recipients)
        if not compatible:
            record(donation, "unassigned", (
                f"Donation {donation.id} could not be assigned because no recipient "
                f"accepts '{donation.food_type}' in area '{donation.pickup_area}' "
                f"that is open at minute {donation.ready_time}."
            ), order_matters=False)
            continue

        recipient = _find_feasible_recipient(donation, recipients, remaining_capacity)
        if recipient is None:
            record(donation, "unassigned", (
                f"Donation {donation.id} could not be assigned because the recipients "
                f"that accept '{donation.food_type}' in area '{donation.pickup_area}' "
                f"do not have {donation.quantity} units of capacity remaining."
            ))
            continue

        volunteer = _find_feasible_volunteer(donation, recipient.area, volunteers, pickups_used)
        if volunteer is None:
            record(donation, "unassigned", (
                f"Donation {donation.id} could not be assigned because no "
                f"available volunteer in area '{recipient.area}' had enough "
                f"vehicle capacity or remaining pickups."
            ))
            continue

        remaining_capacity[recipient.id] -= donation.quantity
        pickups_used[volunteer.id] += 1
        record(donation, "assigned", (
            f"Donation {donation.id} was assigned to {recipient.name} with "
            f"volunteer {volunteer.id} because it had {donation.shelf_life_minutes} "
            f"minutes of shelf life remaining, the recipient accepts "
            f"'{donation.food_type}' with available capacity, and the volunteer "
            f"could carry the quantity ({donation.quantity})."
        ), recipient_id=recipient.id, volunteer_id=volunteer.id, quantity=donation.quantity)

    return allocations