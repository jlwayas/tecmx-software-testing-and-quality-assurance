"""
compute_statistics.py

Compute descriptive
(mean, median, mode, variance, standard deviation)
from a text file containing one number per line.

The program:
- Is invoked from the command line and receives the input file path.
- Skips invalid lines, reports them to the console, and continues execution.
- Prints results to the console and writes them to StatisticsResults.txt.
- Uses basic algorithms only (no statistics libraries).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

import math
import sys
import time


RESULTS_FILENAME = "StatisticsResults.txt"


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class StatsResult:
    """Container for computed statistics and metadata."""
    count: int
    invalid_count: int
    avg: float
    med: float
    modes: List[float]
    mode_freq: int
    var: float
    std: float
    elapsed_seconds: float



def read_numbers_from_file(filepath: str) -> Tuple[List[float], int]:
    """
    Reads numbers from a text file (one per line).
    Invalid lines are reported to the console and skipped.

    Args:
        filepath: Input file path.

    Returns:
        (numbers, invalid_count)
    """
    numbers: List[float] = []
    invalid_count = 0

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line_no, raw_line in enumerate(file, start=1):
                line = raw_line.strip()

                if not line:
                    invalid_count += 1
                    print(
                        f"[ERROR] Line {line_no}: empty/blank line. Skipping."
                    )
                    continue

                try:
                    value = float(line)
                    if math.isfinite(value):
                        numbers.append(value)
                    else:
                        invalid_count += 1
                        print(
                            f"[ERROR] Line {line_no}: "
                            "non-finite value '{line}'. "
                            "Skipping."
                        )
                except ValueError:
                    invalid_count += 1
                    print(
                        f"[ERROR] Line {line_no}: "
                        "not a number '{line}'. Skipping."
                    )

    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)
    except PermissionError:
        print(f"[ERROR] No permissions to read the file: {filepath}")
        sys.exit(1)

    return numbers, invalid_count


def mean(values: List[float]) -> float:
    """Computes the arithmetic mean."""
    total = 0.0
    for v in values:
        total += v
    return total / len(values)


def median(values: List[float]) -> float:
    """Computes the median (sorts internally)."""
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2

    if n % 2 == 1:
        return sorted_vals[mid]

    return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0


def mode(values: List[float]) -> Tuple[List[float], int]:
    """
    Computes the mode(s) using basic counting.

    Note: For floating-point data, many values may be unique.
    In this implementation, if the maximum frequency is 1, we report "no mode".
    Otherwise, all values tied with the maximum frequency are returned.

    Returns:
        (modes, frequency)
    """
    freq: Dict[float, int] = {}
    for value in values:
        freq[value] = freq.get(value, 0) + 1

    max_count = max(freq.values())

    if max_count <= 1:
        return [], 1

    modes: List[float] = []
    for value, count in freq.items():
        if count == max_count:
            modes.append(value)

    modes.sort()
    return modes, max_count


def variance(values: List[float], avg: float) -> float:
    """
    Computes population variance (divides by N).

    If you need sample variance, change the divisor to (N - 1)
    and ensure N > 1.
    """
    total = 0.0
    for value in values:
        diff = value - avg
        total += diff * diff
    return total / len(values)


def std_deviation(var: float) -> float:
    """Computes standard deviation from variance."""
    return math.sqrt(var)


def format_results(result: StatsResult) -> str:
    """Builds the final output text for console/file."""
    lines: List[str] = []
    lines.append("=== Statistical Results ===")
    lines.append(f"Valid data count: {result.count}")
    lines.append(f"Invalid data count: {result.invalid_count}")
    lines.append("")
    lines.append(f"Mean: {result.avg}")
    lines.append(f"Median: {result.med}")

    if not result.modes:
        lines.append("Mode: No mode (all frequencies are 1).")
    else:
        lines.append(f"Mode(s) (frequency {result.mode_freq}): {result.modes}")

    lines.append(f"Variance: {result.var}")
    lines.append(f"Standard deviation: {result.std}")
    lines.append("")
    lines.append(f"Elapsed time (s): {result.elapsed_seconds:.6f}")

    return "\n".join(lines) + "\n"


def write_results(output_text: str, filename: str = RESULTS_FILENAME) -> None:
    """Escribe resultados a un archivo."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(output_text)


def main() -> None:
    """Entry Point"""
    start = time.perf_counter()

    if len(sys.argv) < 2:
        print("[ERROR] missing parameter: "
              "python3 compute_statistics.py fileWithData.txt")
        sys.exit(1)

    filepath = sys.argv[1]
    numbers, invalid_count = read_numbers_from_file(filepath)

    if not numbers:
        elapsed = time.perf_counter() - start
        output = (
            "=== Statistical Results ===\n"
            "No valid data to process.\n"
            f"Invalid data count: {invalid_count}\n"
            f"Elapsed time (s): {elapsed:.6f}\n"
        )
        print(output, end="")
        write_results(output)
        sys.exit(0)

    avg = mean(numbers)
    med = median(numbers)
    modes, mode_freq = mode(numbers)
    var = variance(numbers, avg)
    std = std_deviation(var)

    elapsed = time.perf_counter() - start

    result = StatsResult(
        count=len(numbers),
        invalid_count=invalid_count,
        avg=avg,
        med=med,
        modes=modes,
        mode_freq=mode_freq,
        var=var,
        std=std,
        elapsed_seconds=elapsed,
    )

    output = format_results(result)

    print(output, end="")
    write_results(output)


if __name__ == "__main__":
    main()
