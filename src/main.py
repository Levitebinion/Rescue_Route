"""Command-line entry point for RescueRoute."""

import argparse

from .fifo import allocate_fifo
from .greedy import allocate_greedy
from .loader import load_donations, load_recipients
from .metrics import allocation_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Match donated supplies to recipients.")
    parser.add_argument("--donations", required=True)
    parser.add_argument("--recipients", required=True)
    parser.add_argument("--strategy", choices=("fifo", "greedy"), default="fifo")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    donations = load_donations(args.donations)
    recipients = load_recipients(args.recipients)
    allocator = allocate_fifo if args.strategy == "fifo" else allocate_greedy
    allocations = allocator(donations, recipients)
    for allocation in allocations:
        print(f"{allocation.item}: {allocation.quantity} -> {allocation.recipient_id}")
    print(allocation_summary(allocations, recipients))


if __name__ == "__main__":
    main()