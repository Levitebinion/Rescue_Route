from src.fifo import allocate_fifo
from tests.helpers import make_donation, make_recipient, make_volunteer


def test_normal_case_assigns_donation():
    allocations = allocate_fifo([make_donation()], [make_recipient()], [make_volunteer()])
    assert len(allocations) == 1
    assert allocations[0].status == "assigned"
    assert allocations[0].recipient_id == "r1"
    assert allocations[0].volunteer_id == "v1"
    assert allocations[0].quantity == 10


def test_expired_donation_is_unassigned():
    allocations = allocate_fifo([make_donation(shelf_life=0)], [make_recipient()], [make_volunteer()])
    assert allocations[0].status == "unassigned"
    assert "expired" in allocations[0].decision_reason


def test_no_compatible_food_type_is_unassigned():
    allocations = allocate_fifo(
        [make_donation(food_type="seafood")],
        [make_recipient(food_types={"produce"})],
        [make_volunteer()],
    )
    assert allocations[0].status == "unassigned"
    assert "no recipient accepts" in allocations[0].decision_reason


def test_insufficient_recipient_capacity_is_unassigned():
    allocations = allocate_fifo(
        [make_donation(quantity=50)], [make_recipient(capacity=10)], [make_volunteer()]
    )
    assert allocations[0].status == "unassigned"


def test_recipient_closed_before_ready_time_is_unassigned():
    allocations = allocate_fifo(
        [make_donation(ready_time=100)], [make_recipient(closing_time=50)], [make_volunteer()]
    )
    assert allocations[0].status == "unassigned"


def test_no_volunteer_with_enough_vehicle_capacity_is_unassigned():
    allocations = allocate_fifo(
        [make_donation(quantity=10)], [make_recipient()], [make_volunteer(capacity=5)]
    )
    assert allocations[0].status == "unassigned"
    assert "no available volunteer" in allocations[0].decision_reason


def test_unavailable_volunteer_is_skipped():
    allocations = allocate_fifo(
        [make_donation()], [make_recipient()], [make_volunteer(available=False)]
    )
    assert allocations[0].status == "unassigned"


def test_volunteer_max_pickups_is_enforced():
    donations = [make_donation("d1", quantity=5), make_donation("d2", quantity=5)]
    allocations = allocate_fifo(donations, [make_recipient()], [make_volunteer(max_pickups=1)])
    assert [a.status for a in allocations] == ["assigned", "unassigned"]


def test_two_donations_compete_for_same_capacity_first_arrival_wins():
    donations = [make_donation("d1", quantity=30), make_donation("d2", quantity=30)]
    allocations = allocate_fifo(donations, [make_recipient(capacity=40)], [make_volunteer()])
    assert [a.status for a in allocations] == ["assigned", "unassigned"]


def test_each_donation_gets_exactly_one_decision_and_is_not_split():
    donations = [make_donation(quantity=40)]
    recipients = [make_recipient("r1", capacity=20), make_recipient("r2", capacity=30)]
    allocations = allocate_fifo(donations, recipients, [make_volunteer()])
    assert len(allocations) == 1
    assert allocations[0].status == "unassigned"


def test_empty_inputs_return_no_allocations():
    assert allocate_fifo([], [make_recipient()], [make_volunteer()]) == []
    allocations = allocate_fifo([make_donation()], [], [])
    assert allocations[0].status == "unassigned"