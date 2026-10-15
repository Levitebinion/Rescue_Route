from src.fifo import allocate_fifo
from src.greedy import allocate_greedy
from tests.helpers import make_donation, make_recipient, make_volunteer


def _assigned_ids(allocations):
    return [a.donation_id for a in allocations if a.status == "assigned"]


def test_greedy_serves_least_shelf_life_first():
    relaxed = make_donation("relaxed", shelf_life=200, quantity=5)
    urgent = make_donation("urgent", shelf_life=10, quantity=5)
    allocations = allocate_greedy([relaxed, urgent], [make_recipient(capacity=5)], [make_volunteer()])
    assert _assigned_ids(allocations) == ["urgent"]


def test_tie_on_shelf_life_goes_to_larger_quantity():
    small = make_donation("small", shelf_life=50, quantity=5, ready_time=0)
    large = make_donation("large", shelf_life=50, quantity=20, ready_time=10)
    allocations = allocate_greedy([small, large], [make_recipient(capacity=20)], [make_volunteer()])
    assert _assigned_ids(allocations) == ["large"]


def test_tie_on_shelf_life_and_quantity_goes_to_earlier_ready_time():
    late = make_donation("late", shelf_life=50, quantity=10, ready_time=20)
    early = make_donation("early", shelf_life=50, quantity=10, ready_time=5)
    allocations = allocate_greedy([late, early], [make_recipient(capacity=10)], [make_volunteer()])
    assert _assigned_ids(allocations) == ["early"]


def test_fifo_and_greedy_produce_different_results():
    # Same input, one scarce slot. FIFO takes whoever arrived first;
    # greedy takes whoever expires first.
    relaxed = make_donation("relaxed", shelf_life=200, quantity=5)
    urgent = make_donation("urgent", shelf_life=10, quantity=5)
    args = ([relaxed, urgent], [make_recipient(capacity=5)], [make_volunteer()])
    assert _assigned_ids(allocate_fifo(*args)) == ["relaxed"]
    assert _assigned_ids(allocate_greedy(*args)) == ["urgent"]


def test_starvation_long_shelf_life_donation_is_deferred_indefinitely():
    # Fairness/starvation discussion case: a steady stream of urgent donations
    # always outranks the long-shelf-life one, so under greedy it never gets
    # the single scarce slot, even though it arrived first.
    patient = make_donation("patient", shelf_life=500, quantity=10, ready_time=0)
    urgent_stream = [make_donation(f"u{i}", shelf_life=20 + i, quantity=10, ready_time=i + 1) for i in range(3)]
    args = ([patient] + urgent_stream, [make_recipient(capacity=30)], [make_volunteer()])

    assert "patient" in _assigned_ids(allocate_fifo(*args))
    greedy_allocations = allocate_greedy(*args)
    assert "patient" not in _assigned_ids(greedy_allocations)
    assert _assigned_ids(greedy_allocations) == ["u0", "u1", "u2"]


def test_greedy_still_explains_every_donation():
    donations = [make_donation("d1"), make_donation("d2", food_type="seafood")]
    allocations = allocate_greedy(donations, [make_recipient()], [make_volunteer()])
    assert len(allocations) == 2
    assert all(a.decision_reason for a in allocations)