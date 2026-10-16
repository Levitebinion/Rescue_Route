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

def test_deferred_donation_names_the_more_urgent_donation_that_went_first():
    relaxed = make_donation("relaxed", shelf_life=200, quantity=5)   # arrives first
    urgent = make_donation("urgent", shelf_life=10, quantity=5)
    allocations = allocate_greedy([relaxed, urgent], [make_recipient(capacity=5)], [make_volunteer()])
    deferred = next(a for a in allocations if a.donation_id == "relaxed")

    assert deferred.status == "unassigned"
    assert deferred.deferred_after == ("urgent",)
    assert "considered after urgent (less remaining shelf life)" in deferred.decision_reason


def test_deferral_explains_tie_break_on_quantity():
    small = make_donation("small", shelf_life=50, quantity=5)        # arrives first
    large = make_donation("large", shelf_life=50, quantity=20)
    allocations = allocate_greedy([small, large], [make_recipient(capacity=20)], [make_volunteer()])
    deferred = next(a for a in allocations if a.donation_id == "small")
    assert "equal shelf life but a larger quantity" in deferred.decision_reason


def test_donation_processed_in_arrival_order_has_no_deferral():
    urgent = make_donation("urgent", shelf_life=10, quantity=5)      # arrives first AND most urgent
    relaxed = make_donation("relaxed", shelf_life=200, quantity=5)
    allocations = allocate_greedy([urgent, relaxed], [make_recipient(capacity=5)], [make_volunteer()])
    urgent_allocation = next(a for a in allocations if a.donation_id == "urgent")
    assert urgent_allocation.deferred_after == ()
    assert "urgency-first" not in urgent_allocation.decision_reason


def test_deferral_note_ignores_donations_in_other_areas():
    # The eastside donation jumps the queue, but it can't compete with a
    # downtown donation for recipients or volunteers, so it isn't blamed.
    relaxed = make_donation("relaxed", shelf_life=200, quantity=5, area="downtown")
    urgent = make_donation("urgent", shelf_life=10, quantity=5, area="eastside")
    recipients = [make_recipient("r-down", area="downtown"), make_recipient("r-east", area="eastside")]
    volunteers = [make_volunteer("v-down", area="downtown"), make_volunteer("v-east", area="eastside")]

    allocations = allocate_greedy([relaxed, urgent], recipients, volunteers)
    relaxed_allocation = next(a for a in allocations if a.donation_id == "relaxed")

    assert relaxed_allocation.status == "assigned"
    assert relaxed_allocation.deferred_after == ("urgent",)         # processing order did change...
    assert "urgency-first" not in relaxed_allocation.decision_reason  # ...but it did not matter


def test_no_deferral_note_when_failure_has_nothing_to_do_with_order():
    # Nobody accepts seafood, so being processed later is irrelevant.
    seafood = make_donation("seafood", food_type="seafood", shelf_life=200)
    urgent = make_donation("urgent", shelf_life=10)
    allocations = allocate_greedy([seafood, urgent], [make_recipient(food_types={"produce"})], [make_volunteer()])
    seafood_allocation = next(a for a in allocations if a.donation_id == "seafood")
    assert seafood_allocation.status == "unassigned"
    assert "urgency-first" not in seafood_allocation.decision_reason