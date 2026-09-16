from src.fifo import allocate_fifo
from src.models import Donation, Recipient


def test_fifo_consumes_matching_donations_in_order():
    donations = [Donation("d1", "water", 3), Donation("d2", "water", 4)]
    recipients = [Recipient("r1", "A", "water", 5)]
    allocations = allocate_fifo(donations, recipients)
    assert [(item.donation_id, item.quantity) for item in allocations] == [("d1", 3), ("d2", 2)]


def test_fifo_does_not_match_different_items():
    allocations = allocate_fifo([Donation("d1", "water", 4)], [Recipient("r1", "A", "food", 2)])
    assert allocations == []