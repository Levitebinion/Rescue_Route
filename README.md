## RescueRoute

RescueRoute matches donated supplies to recipients and reports fulfillment metrics.

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the test suite with `pytest` and run the CLI with:

```bash
python3 -m src.main --donations data/donations.csv --recipients data/recipients.csv --strategy fifo
```

Use `--strategy greedy` to serve higher-priority recipients first. CSV and JSON input are supported by the loader.
