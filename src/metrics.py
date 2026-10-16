"""Metrics for allocation results."""

from collections.abc import Iterable

from .models import Allocation, Donation, Recipient, Volunteer


def summarize(donations: Iterable[Donation], recipients: Iterable[Recipient], volunteers: Iterable[Volunteer], 
allocations: Iterable[Allocation], urgent_fraction: float = 0.25) -> dict[str, float | int]:
    donations = list(donations)
    recipients = list(recipients)
    volunteers = list(volunteers)
    allocations = list(allocations)

    donation_by_id = {d.id: d for d in donations}
    assigned = [a for a in allocations if a.status == "assigned"]
    unassigned = [a for a in allocations if a.status == "unassigned"]

    quantity_rescued = sum(donation_by_id[a.donation_id].quantity for a in assigned)
    quantity_at_risk = sum(donation_by_id[a.donation_id].quantity for a in unassigned)

    # "Urgent" = the most time-sensitive slice (default: 25%, at least one) of
    # the donations that could still be rescued in time. Donations already
    # expired by their ready time are left out: no strategy can rescue them,
    # so counting them would just drag both strategies' rates toward zero.
    # Adjust urgent_fraction, or the definition, to match your README.
    rescuable = [d for d in donations if d.shelf_life_minutes > d.ready_time]
    by_urgency = sorted(rescuable, key=lambda d: d.shelf_life_minutes)
    cutoff = max(1, round(len(by_urgency) * urgent_fraction)) if by_urgency else 0
    urgent_ids = {d.id for d in by_urgency[:cutoff]}
    assigned_ids = {a.donation_id for a in assigned}
    urgent_rescue_rate = (
        len(urgent_ids & assigned_ids) / len(urgent_ids) if urgent_ids else 0.0
    )

    total_recipient_capacity = sum(r.capacity for r in recipients)
    total_volunteer_capacity = sum(v.vehicle_capacity for v in volunteers)

    return {
        "donations_received": len(donations),
        "donations_assigned": len(assigned),
        "donations_unassigned": len(unassigned),
        "food_quantity_rescued": quantity_rescued,
        "food_quantity_at_risk": quantity_at_risk,
        "urgent_rescue_rate": round(urgent_rescue_rate, 4),
        "recipient_capacity_utilization": (
            round(quantity_rescued / total_recipient_capacity, 4) if total_recipient_capacity else 0.0
        ),
        "volunteer_capacity_utilization": (
            round(quantity_rescued / total_volunteer_capacity, 4) if total_volunteer_capacity else 0.0
        ),
    }


def compare_strategies(fifo_summary: dict[str, float | int],
                        greedy_summary: dict[str, float | int]) -> dict[str, float | int]:
    """Difference in assigned donations, rescued quantity, and urgent rescue
    rate between the two strategies (greedy minus fifo)."""
    return {
        "assigned_diff": greedy_summary["donations_assigned"] - fifo_summary["donations_assigned"],
        "quantity_rescued_diff": greedy_summary["food_quantity_rescued"] - fifo_summary["food_quantity_rescued"],
        "urgent_rescue_rate_diff": round(
            greedy_summary["urgent_rescue_rate"] - fifo_summary["urgent_rescue_rate"], 4
        ),
    }