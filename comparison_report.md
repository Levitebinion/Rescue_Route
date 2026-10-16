# FIFO vs Greedy Comparison

## Processing order

- FIFO (arrival order): D-1001, D-1002, D-1003, D-1004, D-1005, D-1006, D-1007, D-1008, D-1009
- Greedy (urgency-first): D-1004, D-1007, D-1002, D-1009, D-1006, D-1008, D-1003, D-1005, D-1001

## Metrics

| Metric | FIFO | Greedy | Greedy - FIFO |
|---|---|---|---|
| donations_received | 9 | 9 | 0 |
| donations_assigned | 4 | 4 | 0 |
| donations_unassigned | 5 | 5 | 0 |
| food_quantity_rescued | 100 | 97 | -3 |
| food_quantity_at_risk | 79 | 82 | 3 |
| urgent_rescue_rate | 0.0 | 1.0 | 1.0 |
| recipient_capacity_utilization | 0.7692 | 0.7462 | -0.023 |
| volunteer_capacity_utilization | 0.7407 | 0.7185 | -0.0222 |

## Donations handled differently

### D-1001: assigned under FIFO only

- FIFO: Donation D-1001 was assigned to Community Shelter with volunteer V-301 because it had 300 minutes of shelf life remaining, the recipient accepts 'produce' with available capacity, and the volunteer could carry the quantity (25).
- Greedy: Donation D-1001 could not be assigned because the recipients that accept 'produce' in area 'downtown' do not have 25 units of capacity remaining. Under the urgency-first rule it was considered after D-1002 (less remaining shelf life) and D-1006 (less remaining shelf life), which were assigned first even though this donation arrived earlier.

### D-1002: assigned under greedy only

- FIFO: Donation D-1002 could not be assigned because the recipients that accept 'prepared_meals' in area 'downtown' do not have 20 units of capacity remaining.
- Greedy: Donation D-1002 was assigned to Community Shelter with volunteer V-301 because it had 45 minutes of shelf life remaining, the recipient accepts 'prepared_meals' with available capacity, and the volunteer could carry the quantity (20).

### D-1008: assigned under FIFO only

- FIFO: Donation D-1008 was assigned to Westside Kitchen with volunteer V-304 because it had 150 minutes of shelf life remaining, the recipient accepts 'bread' with available capacity, and the volunteer could carry the quantity (20).
- Greedy: Donation D-1008 could not be assigned because the recipients that accept 'bread' in area 'westside' do not have 20 units of capacity remaining. Under the urgency-first rule it was considered after D-1009 (less remaining shelf life), which was assigned first even though this donation arrived earlier.

### D-1009: assigned under greedy only

- FIFO: Donation D-1009 could not be assigned because the recipients that accept 'prepared_meals' in area 'westside' do not have 22 units of capacity remaining.
- Greedy: Donation D-1009 was assigned to Westside Kitchen with volunteer V-304 because it had 75 minutes of shelf life remaining, the recipient accepts 'prepared_meals' with available capacity, and the volunteer could carry the quantity (22).

## Summary

- Greedy rescued 2 donation(s) FIFO did not: D-1002, D-1009 (42 units).
- FIFO rescued 2 donation(s) greedy did not: D-1001, D-1008 (45 units). This is the trade-off of the urgency-first rule: capacity went to more urgent donations, so a longer-lasting donation lost out.
- Urgent rescue rate: FIFO 0.0 vs greedy 1.0.
- Both strategies use identical feasibility checks; only the processing order differs, so each difference above comes from which donation reached scarce recipient capacity or volunteer pickups first.
