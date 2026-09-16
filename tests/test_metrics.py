from src.metrics import allocation_summary, fulfillment_rate, total_allocated
from src.models import Allocation, Recipient


def test_metrics_report_partial_fulfillment():
    allocations = [Allocation("d1", "r1", "water", 3)]
    recipients = [Recipient("r1", "A", "water", 5)]
    assert total_allocated(allocations) == 3
    assert fulfillment_rate(allocations, recipients) == 0.6
    assert allocation_summary(allocations, recipients)["allocation_count"] == 1