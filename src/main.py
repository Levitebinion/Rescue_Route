"""Command-line entry point for RescueRoute."""

import argparse
from pathlib import Path

from .fifo import allocate_fifo
from .greedy import allocate_greedy
from .loader import load_donations, load_recipients, load_volunteers
from .metrics import compare_strategies, summarize
from .report import build_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Match donated food to recipients and volunteers.")
    parser.add_argument("--donations", required=True)
    parser.add_argument("--recipients", required=True)
    parser.add_argument("--volunteers", required=True)
    parser.add_argument("--strategy", choices=("fifo", "greedy", "both"), default="both")
    parser.add_argument("--report", help="Write a FIFO-vs-greedy Markdown report to this path (needs --strategy both).")
    return parser


def _run(strategy_name: str, allocator, donations, recipients, volunteers):
    allocations = allocator(donations, recipients, volunteers)
    print(f"\n=== {strategy_name.upper()} Results ===")
    for allocation in allocations:
        print(f"[{allocation.status.upper()}] {allocation.decision_reason}")
    summary = summarize(donations, recipients, volunteers, allocations)
    print(f"\n--- {strategy_name.upper()} Metrics ---")
    for key, value in summary.items():
        print(f"{key}: {value}")
    return allocations, summary


def main() -> None:
    args = build_parser().parse_args()
    donations = load_donations(args.donations)
    recipients = load_recipients(args.recipients)
    volunteers = load_volunteers(args.volunteers)

    results = {}
    if args.strategy in ("fifo", "both"):
        results["fifo"] = _run("fifo", allocate_fifo, donations, recipients, volunteers)
    if args.strategy in ("greedy", "both"):
        results["greedy"] = _run("greedy", allocate_greedy, donations, recipients, volunteers)

    if args.strategy == "both":
        fifo_allocations, fifo_summary = results["fifo"]
        greedy_allocations, greedy_summary = results["greedy"]
        print("\n=== FIFO vs Greedy Comparison ===")
        for key, value in compare_strategies(fifo_summary, greedy_summary).items():
            print(f"{key}: {value}")
        if args.report:
            report = build_report(donations, fifo_allocations, greedy_allocations,
                                  fifo_summary, greedy_summary)
            Path(args.report).write_text(report, encoding="utf-8")
            print(f"\nReport written to {args.report}")
    elif args.report:
        print("\n--report needs --strategy both; no report written.")


if __name__ == "__main__":
    main()