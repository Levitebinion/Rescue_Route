"""Guards the demo dataset in data/: if someone edits the CSVs, the demo
should still show FIFO and greedy disagreeing, with every decision explained."""

from pathlib import Path

from src.fifo import allocate_fifo
from src.greedy import allocate_greedy
from src.loader import load_donations, load_recipients, load_volunteers
from src.metrics import summarize

DATA = Path(__file__).resolve().parents[1] / "data"


def _load():
    return (load_donations(DATA / "donations.csv"),
            load_recipients(DATA / "recipients.csv"),
            load_volunteers(DATA / "volunteers.csv"))


def _assigned(allocations):
    return {a.donation_id for a in allocations if a.status == "assigned"}


def test_sample_data_loads_and_every_donation_is_explained():
    donations, recipients, volunteers = _load()
    for allocate in (allocate_fifo, allocate_greedy):
        allocations = allocate(donations, recipients, volunteers)
        assert len(allocations) == len(donations)
        assert all(a.decision_reason for a in allocations)


def test_sample_data_makes_fifo_and_greedy_disagree():
    donations, recipients, volunteers = _load()
    fifo = allocate_fifo(donations, recipients, volunteers)
    greedy = allocate_greedy(donations, recipients, volunteers)
    assert _assigned(fifo) != _assigned(greedy)

    fifo_summary = summarize(donations, recipients, volunteers, fifo)
    greedy_summary = summarize(donations, recipients, volunteers, greedy)
    assert greedy_summary["urgent_rescue_rate"] > fifo_summary["urgent_rescue_rate"]


def test_sample_data_covers_each_failure_reason():
    donations, recipients, volunteers = _load()
    reasons = " ".join(a.decision_reason for a in allocate_fifo(donations, recipients, volunteers))
    assert "already expired" in reasons
    assert "not ready for pickup" in reasons
    assert "no recipient accepts" in reasons
    assert "capacity remaining" in reasons