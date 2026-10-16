"""Command-line entry point for RescueRoute."""

import argparse

from .fifo import allocate_fifo
from .greedy import allocate_greedy
from .loader import load_donations, load_recipients, load_volunteers
from .metrics import compare_strategies, summarize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Match donated food to recipients and volunteers.")
    parser.add_argument("--donations", required=True)
    parser.add_argument("--recipients", required=True)
    parser.add_argument("--volunteers", required=True)
    parser.add_argument("--strategy", choices=("fifo", "greedy", "both"), default="both")
    return parser


def _run(strategy_name: str, allocator, donations, recipients, volunteers) -> dict:
    allocations = allocator(donations, recipients, volunteers)
    print(f"\n=== {strategy_name.upper()} Results ===")
    for allocation in allocations:
        print(f"[{allocation.status.upper()}] {allocation.decision_reason}")
    summary = summarize(donations, recipients, volunteers, allocations)
    print(f"\n--- {strategy_name.upper()} Metrics ---")
    for key, value in summary.items():
        print(f"{key}: {value}")
    return summary


def main() -> None:
    args = build_parser().parse_args()
    donations = load_donations(args.donations)
    recipients = load_recipients(args.recipients)
    volunteers = load_volunteers(args.volunteers)

    summaries = {}
    if args.strategy in ("fifo", "both"):
        summaries["fifo"] = _run("fifo", allocate_fifo, donations, recipients, volunteers)
    if args.strategy in ("greedy", "both"):
        summaries["greedy"] = _run("greedy", allocate_greedy, donations, recipients, volunteers)

    if args.strategy == "both":
        print("\n=== FIFO vs Greedy Comparison ===")
        for key, value in compare_strategies(summaries["fifo"], summaries["greedy"]).items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()