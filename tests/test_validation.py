import pytest

from src.loader import load_donations
from src.validation import (
    validate_donation,
    validate_recipient,
    validate_unique_ids,
    validate_volunteer,
)
from tests.helpers import make_donation, make_recipient, make_volunteer


def test_valid_records_are_returned():
    donation = make_donation()
    assert validate_donation(donation) == donation
    assert validate_recipient(make_recipient())
    assert validate_volunteer(make_volunteer())


def test_quantity_must_be_positive():
    with pytest.raises(ValueError, match="positive"):
        validate_donation(make_donation(quantity=0))


def test_shelf_life_cannot_be_negative():
    with pytest.raises(ValueError, match="non-negative"):
        validate_donation(make_donation(shelf_life=-5))


def test_recipient_needs_at_least_one_food_type():
    with pytest.raises(ValueError, match="accepted_food_types"):
        validate_recipient(make_recipient(food_types=frozenset()))


def test_volunteer_vehicle_capacity_must_be_positive():
    with pytest.raises(ValueError, match="positive"):
        validate_volunteer(make_volunteer(capacity=0))


def test_ids_must_be_unique():
    with pytest.raises(ValueError, match="duplicate"):
        validate_unique_ids([make_donation("d1"), make_donation("d1", food_type="dairy")])


def test_loader_rejects_duplicate_donation_ids(tmp_path):
    path = tmp_path / "donations.csv"
    path.write_text(
        "id,donor_name,food_type,quantity,shelf_life_minutes,pickup_area,ready_time\n"
        "d1,Donor,produce,10,60,downtown,0\n"
        "d1,Donor,produce,10,60,downtown,0\n"
    )
    with pytest.raises(ValueError, match="duplicate"):
        load_donations(path)


def test_loader_handles_empty_file(tmp_path):
    path = tmp_path / "donations.csv"
    path.write_text("id,donor_name,food_type,quantity,shelf_life_minutes,pickup_area,ready_time\n")
    assert load_donations(path) == []