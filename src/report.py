"""Plain-text (Markdown) FIFO-vs-greedy comparison report.

The matching engine is identical for both strategies; only the processing
order differs. So every difference in outcome comes from which donation
reached a scarce recipient capacity or volunteer pickup first -- the report
shows each differing donation with both strategies' own explanations.
"""

from collections.abc import Iterable

from .models import Allocation, Donation


def _signature(allocation: Allocation) -> tuple:
    return (allocation.status, allocation.recipient_id, allocation.volunteer_id)


def _headline(fifo: Allocation, greedy: Allocation) -> str:
    if fifo.status == "unassigned" and greedy.status == "assigned":
        return "assigned under greedy only"
    if fifo.status == "assigned" and greedy.status == "unassigned":
        return "assigned under FIFO only"
    return "assigned to a different recipient/volunteer"


def _quantity(ids: list[str], quantity_by_id: dict[str, int]) -> int:
    return sum(quantity_by_id[i] for i in ids)


def build_report(donations: Iterable[Donation], fifo_allocations: Iterable[Allocation],
                 greedy_allocations: Iterable[Allocation], fifo_summary: dict,
                 greedy_summary: dict) -> str:
    donations = list(donations)
    fifo_allocations = list(fifo_allocations)
    greedy_allocations = list(greedy_allocations)
    quantity_by_id = {d.id: d.quantity for d in donations}
    fifo_by_id = {a.donation_id: a for a in fifo_allocations}
    greedy_by_id = {a.donation_id: a for a in greedy_allocations}

    lines = ["# FIFO vs Greedy Comparison", ""]

    lines += ["## Processing order", "",
              f"- FIFO (arrival order): {', '.join(d.id for d in donations) or '(none)'}",
              f"- Greedy (urgency-first): {', '.join(a.donation_id for a in greedy_allocations) or '(none)'}",
              ""]

    lines += ["## Metrics", "", "| Metric | FIFO | Greedy | Greedy - FIFO |", "|---|---|---|---|"]
    for key, fifo_value in fifo_summary.items():
        greedy_value = greedy_summary[key]
        lines.append(f"| {key} | {fifo_value} | {greedy_value} | {round(greedy_value - fifo_value, 4)} |")
    lines.append("")

    differing = [d.id for d in donations if _signature(fifo_by_id[d.id]) != _signature(greedy_by_id[d.id])]
    lines += ["## Donations handled differently", ""]
    if not differing:
        lines += ["Both strategies produced identical outcomes for every donation on this input.", ""]
    for donation_id in differing:
        fifo, greedy = fifo_by_id[donation_id], greedy_by_id[donation_id]
        lines += [f"### {donation_id}: {_headline(fifo, greedy)}", "",
                  f"- FIFO: {fifo.decision_reason}",
                  f"- Greedy: {greedy.decision_reason}", ""]

    greedy_only = [i for i in differing if fifo_by_id[i].status == "unassigned" and greedy_by_id[i].status == "assigned"]
    fifo_only = [i for i in differing if fifo_by_id[i].status == "assigned" and greedy_by_id[i].status == "unassigned"]
    lines += ["## Summary", ""]
    if greedy_only:
        lines.append(f"- Greedy rescued {len(greedy_only)} donation(s) FIFO did not: "
                     f"{', '.join(greedy_only)} ({_quantity(greedy_only, quantity_by_id)} units).")
    if fifo_only:
        lines.append(f"- FIFO rescued {len(fifo_only)} donation(s) greedy did not: "
                     f"{', '.join(fifo_only)} ({_quantity(fifo_only, quantity_by_id)} units). "
                     f"This is the trade-off of the urgency-first rule: capacity went to more "
                     f"urgent donations, so a longer-lasting donation lost out.")
    if not greedy_only and not fifo_only:
        lines.append("- The same donations were rescued under both strategies.")
    lines.append(
        f"- Urgent rescue rate: FIFO {fifo_summary['urgent_rescue_rate']} vs "
        f"greedy {greedy_summary['urgent_rescue_rate']}."
    )
    lines.append(
        "- Both strategies use identical feasibility checks; only the processing order differs, "
        "so each difference above comes from which donation reached scarce recipient capacity "
        "or volunteer pickups first."
    )
    lines.append("")
    return "\n".join(lines)