from src.greedy import allocate_greedy
from src.models import Donation, Recipient


def test_greedy_serves_highest_priority_first():
    donations = [Donation("d1", "water", 5)]
    recipients = [
        Recipient("low", "Low", "water", 5, priority=1),
        Recipient("high", "High", "water", 5, priority=10),
    ]
    allocations = allocate_greedy(donations, recipients)
    assert allocations[0].recipient_id == "high"
    assert allocations[0].quantity == 5