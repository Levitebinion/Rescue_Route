"""Shared factory functions so each test only spells out what it cares about."""

from src.models import Donation, Recipient, Volunteer


def make_donation(id="d1", food_type="produce", quantity=10, shelf_life=60, area="downtown", ready_time=0):
    return Donation(id=id, donor_name="Donor", food_type=food_type, quantity=quantity,
                    shelf_life_minutes=shelf_life, pickup_area=area, ready_time=ready_time)


def make_recipient(id="r1", food_types=frozenset({"produce"}), capacity=100, area="downtown", closing_time=300):
    return Recipient(id=id, name="Org " + id, accepted_food_types=frozenset(food_types), capacity=capacity, area=area, closing_time=closing_time)


def make_volunteer(id="v1", capacity=100, area="downtown", available=True, max_pickups=5):
    return Volunteer(id=id, name="Vol " + id, vehicle_capacity=capacity, area=area, available=available, max_pickups=max_pickups)