# RescueRoute

**CPSC 335 Group Project: Surplus Food Matching & Pickup Planner**

RescueRoute is an explainable Python prototype that matches time-sensitive surplus food donations to compatible recipient organizations and volunteer drivers. It runs two strategies on the same input (a FIFO baseline and an urgency-first greedy strategy) and explains every decision in plain English.

> **This is an educational prototype using simulated data.** It is not food-safety certified, clinically validated, or approved for real food-handling, medical, or emergency operations.

**Central question:** How can we prioritize time-sensitive food donations and assign them to compatible recipients and volunteers in a way that is efficient, transparent, and easy to explain?

---

## Quick start

Requires Python 3.10 or newer.

```bash
pip install pytest

# Run both strategies, print explanations and metrics, and write the comparison report
python3 -m src.main \
  --donations data/donations.csv \
  --recipients data/recipients.csv \
  --volunteers data/volunteers.csv \
  --report comparison_report.md

# Run the tests
python3 -m pytest tests -v
```

Options: `--strategy fifo|greedy|both` (default `both`). `--report PATH` needs `--strategy both`. Input files may be `.csv` or `.json`.

## Project layout

```
Rescue_Route/
├── src/
│   ├── models.py        # Donation, Recipient, Volunteer, Allocation (frozen dataclasses)
│   ├── loader.py        # CSV/JSON -> model objects
│   ├── validation.py    # field checks and duplicate-ID detection
│   ├── matching.py      # shared matching engine: feasibility checks + explanations
│   ├── fifo.py          # FIFO baseline (arrival order)
│   ├── greedy.py        # urgency-first greedy (priority order + deferral logic)
│   ├── metrics.py       # required metrics and strategy comparison
│   ├── report.py        # FIFO-vs-greedy Markdown report
│   └── main.py          # command-line interface
├── data/                # sample CSV inputs (simulated)
├── tests/               # pytest suite (+ helpers.py factory functions)
└── README.md
```

**Design idea:** FIFO and greedy use the *same* matching engine (`matching.py`). The only difference between them is the order in which donations are processed. That keeps the comparison fair, since any difference in outcome comes from ordering alone.

---

## Data model

All times are **minutes since the simulation started (minute 0)**.

| Entity | CSV columns |
|---|---|
| **Donation** | `id, donor_name, food_type, quantity, shelf_life_minutes, pickup_area, ready_time` |
| **Recipient** | `id, name, accepted_food_types, capacity, area, closing_time` (`accepted_food_types` is pipe-separated, e.g. `bread\|produce`) |
| **Volunteer** | `id, name, vehicle_capacity, area, available, max_pickups` |
| **Allocation** (output) | `donation_id, recipient_id, volunteer_id, quantity, decision_reason, status, deferred_after` |

- `shelf_life_minutes` is the shelf life remaining at minute 0. A donation that is not ready for pickup until `ready_time >= shelf_life_minutes` has expired before it can be collected.
- `status` is `assigned` or `unassigned`. `deferred_after` lists donations that were processed ahead of this one even though they arrived later (greedy only).
- `Recipient` also has an optional `priority` field that is loaded but not used by either strategy.

### Sample inputs

`data/` contains a 9-donation scenario built to exercise every outcome: clean matches, an expired donation, a donation that expires before it is ready, a food type nobody accepts, capacity conflicts, and cases where FIFO and greedy disagree.

---

## Data & matching layer

### Validation (`validation.py`, `loader.py`)

- Text fields (IDs, names, food type, areas) must be non-empty.
- `quantity`, recipient `capacity`, `vehicle_capacity`, and `max_pickups` must be positive integers.
- `shelf_life_minutes`, `ready_time`, and `closing_time` must be non-negative integers.
- `accepted_food_types` must contain at least one type; `available` is parsed as a boolean (`true/false`, `yes/no`, `1/0`).
- IDs must be unique within each file; a duplicate raises `ValueError` (detected with a `set`).
- Empty input files load as empty lists and produce empty results.

### Feasibility rules (`matching.py`)

A donation is matched to **one** recipient and **one** volunteer, or rejected with a reason. Checks run in this order:

1. **Expiry:** rejected if it has no shelf life left, or if `ready_time >= shelf_life_minutes`.
2. **Compatible recipient:** the recipient must accept the food type, be in the donation's pickup area, and still be open (`ready_time <= closing_time`).
3. **Recipient capacity:** the recipient's *remaining* capacity must be at least the donation quantity. The first compatible recipient with room (file order) wins.
4. **Volunteer:** must be available, in the same area, have `vehicle_capacity >= quantity`, and have pickups left (`max_pickups`).

Assigning a donation subtracts its quantity from the recipient's remaining capacity and uses up one of the volunteer's pickups. A donation is never split across recipients.

### Data structures

| Where | Structure | Why |
|---|---|---|
| Remaining capacity, pickups used, lookups by ID | `dict` | constant-time lookup by ID |
| Duplicate-ID detection | `set` | constant-time membership test |
| `accepted_food_types` | `frozenset` | set semantics for compatibility; immutable so the frozen dataclass stays hashable |
| FIFO order | list in input order | preserves arrival order |
| Greedy order | list sorted once with a key | the priority rule is a fixed key, so a heap isn't needed |
| Assignment history | list | ordered audit trail |
| Metrics | `dict` | named aggregate values |

---

## Strategies

### A. FIFO baseline

Process donations in arrival order (their order in the input file). For each one, assign the first feasible recipient and volunteer, or record why it could not be assigned.

### B. Greedy urgency-first

Donations are processed in this priority order:

1. **Least remaining shelf life first.**
2. If tied, the **larger quantity** first.
3. If still tied, the **earlier ready time** first.
4. If still tied, **arrival order**.

Each donation then goes through the same feasibility checks and first-fit matching as FIFO.

**What it optimizes locally:** scarce recipient capacity and volunteer pickups go to whichever donation is closest to spoiling.

**Why it's reasonable:** a donation about to expire loses all its value if it waits, while a long-lasting donation can often be placed later.

**Where it can fail:**

- It can rescue **less total food**: spending capacity on a small urgent donation can leave no room for a larger, longer-lasting one.
- It is **first-fit, not best-fit**, so it does not look ahead for a placement that leaves more room for later donations.
- It ignores recipient closing times and distance beyond the exact-area rule.

**Fairness and starvation:** a donation with a long shelf life can be pushed behind every urgent donation and never get capacity, even though it arrived first. A test (`test_starvation_long_shelf_life_donation_is_deferred_indefinitely`) demonstrates this: under FIFO the donation is rescued; under greedy it is deferred behind a stream of urgent ones and left unassigned. A stricter fairness rule (for example, aging) is a possible extension.

---

## Explainability

Every donation, assigned or not, gets a plain-English reason, and greedy adds a sentence when a donation was deferred. Examples from the sample data:

**Assigned:**
> Donation D-1002 was assigned to Community Shelter with volunteer V-301 because it had 45 minutes of shelf life remaining, the recipient accepts 'prepared_meals' with available capacity, and the volunteer could carry the quantity (20).

**Unassigned:**
> Donation D-1007 could not be assigned because it would expire after 30 minutes, but it is not ready for pickup until minute 40.

**Deferred (greedy):**
> Donation D-1001 could not be assigned because the recipients that accept 'produce' in area 'downtown' do not have 25 units of capacity remaining. Under the urgency-first rule it was considered after D-1002 (less remaining shelf life) and D-1006 (less remaining shelf life), which were assigned first even though this donation arrived earlier.

The deferral sentence only names donations that were processed earlier, were assigned, and are in the same area, since only those could have taken the capacity or pickups this donation needed.

---

## Metrics

Reported for both strategies:

| Metric | Definition |
|---|---|
| `donations_received` | total donation records processed |
| `donations_assigned` / `donations_unassigned` | donations with / without a feasible match |
| `food_quantity_rescued` | total quantity of assigned donations |
| `food_quantity_at_risk` | total quantity of unassigned donations |
| `urgent_rescue_rate` | fraction of the **most urgent 25%** (at least one) of *rescuable* donations that were assigned. Donations already expired by their ready time are excluded, since no strategy can rescue them |
| `recipient_capacity_utilization` | quantity rescued ÷ total recipient capacity |
| `volunteer_capacity_utilization` | quantity rescued ÷ total volunteer vehicle capacity |

The 25% cutoff is a documented choice (the `urgent_fraction` argument in `metrics.py`), since the brief does not fix an exact threshold.

## FIFO vs greedy: sample results

On the bundled sample data (`comparison_report.md` has the full per-donation explanations):

| Metric | FIFO | Greedy |
|---|---|---|
| Donations assigned | 4 | 4 |
| Food quantity rescued | 100 | 97 |
| Food quantity at risk | 79 | 82 |
| Urgent rescue rate | 0.0 | 1.0 |
| Recipient capacity utilization | 0.7692 | 0.7462 |
| Volunteer capacity utilization | 0.7407 | 0.7185 |

**What changed and why:** both strategies rescue four donations, but different ones. FIFO takes long-lasting donations that arrived early (D-1001 produce, D-1008 bread), which fills the capacity that two urgent prepared-meal donations (D-1002, D-1009) needed. Greedy reverses this: it rescues both urgent donations and loses the two long-lasting ones, so its urgent rescue rate rises from 0.0 to 1.0 but it saves 3 fewer units overall. Greedy trades total quantity for urgency.

---

## Testing

```bash
python3 -m pytest tests -v
```

| Required case | Covered by |
|---|---|
| Normal compatible match | `test_normal_case_assigns_donation` |
| Duplicate donation ID | `test_ids_must_be_unique`, `test_loader_rejects_duplicate_donation_ids` |
| Expired or nearly expired donation | `test_expired_donation_is_unassigned`, `test_donation_that_expires_before_it_is_ready_is_unassigned` |
| No compatible food type | `test_no_compatible_food_type_is_unassigned` |
| Insufficient recipient capacity | `test_insufficient_recipient_capacity_is_unassigned` |
| No volunteer with enough vehicle capacity | `test_no_volunteer_with_enough_vehicle_capacity_is_unassigned` |
| Two donations competing for capacity | `test_two_donations_compete_for_same_capacity_first_arrival_wins` |
| Empty input | `test_empty_inputs_return_no_allocations`, `test_loader_handles_empty_file` |
| FIFO and greedy differ | `test_fifo_and_greedy_produce_different_results`, `test_sample_data_makes_fifo_and_greedy_disagree` |
| Fairness / starvation | `test_starvation_long_shelf_life_donation_is_deferred_indefinitely` |

Tests build their inputs with the factory functions in `tests/helpers.py`, so each test only states the field it cares about.

---

## Complexity

Let **D** = donations, **R** = recipients, **V** = volunteers.

- **Validation and loading:** O(D + R + V); duplicate detection uses a set.
- **Matching one donation:** finding a compatible recipient scans R and finding a volunteer scans V, so **O(R + V)**.
- **FIFO:** **O(D · (R + V))**.
- **Greedy:** sorting is O(D log D). Working out which donations were deferred compares each donation against those processed before it, which is O(D²) in the worst case. Total: **O(D² + D · (R + V))**.

*Assumptions:* recipients and volunteers are scanned linearly (fine for a prototype; an index keyed by area and food type would cut the scan), and explanation strings are built in constant time per donation.

---

## Limitations

- **Areas are exact-match strings.** A donation, its recipient, and its volunteer must share the same area; there is no distance or routing.
- **One stop per match.** A donation goes to exactly one recipient and is never split.
- **Pickup time is not scheduled separately.** Allocations record the recipient and volunteer but not a distinct scheduled time; a donation is assumed to be picked up at its ready time.
- **Volunteers are limited by a pickup count,** not by time windows, so overlapping trips are not modeled.
- **First-fit matching:** recipients are tried in file order, not chosen to minimize wasted capacity.
- **Greedy can starve long-shelf-life donations** (see above), and no fairness rule is applied.
- **Simulated data only.** Nothing here is a real food-safety or logistics system.

---

## Team

| Role | Member | Responsibilities |
|---|---|---|
| Algorithm & Optimization Lead | _name_ | FIFO scheduler, greedy rule, priority selection, complexity analysis, strategy comparison |
| Data & Matching Lead | Matt | input files, validation, compatibility checks, capacity rules, data structures, test data |
| Product & Quality Lead | _name_ | explainable output, metrics, tests, README, demo materials, CLI polish |

All members share design discussion, code review, debugging, testing, documentation, and the final presentation.

**Individual contributions:** _each member adds a short paragraph here._

---

## References and AI assistance

- Python standard library (`csv`, `json`, `dataclasses`, `argparse`, `pathlib`) and [pytest](https://docs.pytest.org/).
- Course materials for CPSC 335 (greedy algorithms, algorithm analysis).
- **AI-assisted tools:** Claude (Anthropic) was used for code review, refactoring suggestions, drafting tests, and drafting documentation. _[Confirm this matches your course's AI policy and describe exactly what your team did and verified.]_ The team is responsible for understanding, testing, and documenting all submitted code.
