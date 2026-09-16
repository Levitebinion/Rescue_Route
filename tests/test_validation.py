import pytest

from src.models import Donation, Recipient
from src.validation import validate_donation, validate_recipient, validate_unique_ids


def test_valid_records_are_returned():
    donation = Donation("d1", "water", 2)
    assert validate_donation(donation) == donation
    assert validate_recipient(Recipient("r1", "A", "water", 1))


def test_quantity_must_be_positive():
    with pytest.raises(ValueError, match="positive"):
        validate_donation(Donation("d1", "water", 0))


def test_ids_must_be_unique():
    with pytest.raises(ValueError, match="duplicate"):
        validate_unique_ids([Donation("d1", "water", 1), Donation("d1", "food", 1)])