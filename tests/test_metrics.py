from src.fifo import allocate_fifo
from src.greedy import allocate_greedy
from src.metrics import compare_strategies, summarize
from tests.helpers import make_donation, make_recipient, make_volunteer


def test_summary_counts_and_quantities():
    donations = [make_donation("d1", quantity=10), make_donation("d2", food_type="seafood", quantity=99)]
    recipients = [make_recipient(capacity=50)]
    volunteers = [make_volunteer(capacity=50)]
    allocations = allocate_fifo(donations, recipients, volunteers)

    summary = summarize(donations, recipients, volunteers, allocations)

    assert summary["donations_received"] == 2
    assert summary["donations_assigned"] == 1
    assert summary["donations_unassigned"] == 1
    assert summary["food_quantity_rescued"] == 10
    assert summary["food_quantity_at_risk"] == 99
    assert summary["recipient_capacity_utilization"] == 0.2   # 10 / 50
    assert summary["volunteer_capacity_utilization"] == 0.2   # 10 / 50


def test_summary_of_empty_input_does_not_divide_by_zero():
    summary = summarize([], [], [], [])
    assert summary["donations_received"] == 0
    assert summary["recipient_capacity_utilization"] == 0.0
    assert summary["urgent_rescue_rate"] == 0.0


def test_compare_strategies_shows_greedy_rescuing_the_urgent_donation():
    donations = [make_donation("relaxed", shelf_life=200, quantity=5), make_donation("urgent", shelf_life=10, quantity=5)]
    recipients = [make_recipient(capacity=5)]
    volunteers = [make_volunteer()]

    fifo = summarize(donations, recipients, volunteers, allocate_fifo(donations, recipients, volunteers))
    greedy = summarize(donations, recipients, volunteers, allocate_greedy(donations, recipients, volunteers))

    assert fifo["urgent_rescue_rate"] == 0.0
    assert greedy["urgent_rescue_rate"] == 1.0
    diff = compare_strategies(fifo, greedy)
    assert diff["urgent_rescue_rate_diff"] == 1.0
    assert diff["assigned_diff"] == 0

def test_urgent_rescue_rate_ignores_donations_that_could_never_be_rescued():
    # The expired donation is the "most urgent" by shelf life, but nobody can
    # rescue it. The urgent set should be the most urgent *rescuable* donation.
    donations = [make_donation("expired", shelf_life=0),
                 make_donation("urgent", shelf_life=10),
                 make_donation("relaxed", shelf_life=200)]
    recipients = [make_recipient(capacity=100)]
    volunteers = [make_volunteer(max_pickups=5)]
    allocations = allocate_greedy(donations, recipients, volunteers)

    summary = summarize(donations, recipients, volunteers, allocations)
    assert summary["urgent_rescue_rate"] == 1.0