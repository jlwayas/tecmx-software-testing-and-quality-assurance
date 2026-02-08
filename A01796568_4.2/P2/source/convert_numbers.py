"""
convertNumbers.py

Reads a text file containing numbers (one per line) and converts each valid
integer to binary and hexadecimal using basic algorithms only.

Requirements:
- Invoked from the command line with the input file path as a parameter.
- Converts numbers to base-2 (binary) and base-16 (hexadecimal).
- Prints results to the console and writes them to ConvertionResults.txt.
- Handles invalid data gracefully (reports issues and continues).
- Uses basic algorithms only (no bin(), hex(), format(), or conversion libs).
- Measures elapsed time (read + compute) and reports it in console and file.
- PEP8 compliant.
"""

from __future__ import annotations

import sys
import time
from typing import List, Tuple


RESULTS_FILENAME = "ConvertionResults.txt"
HEX_DIGITS = "0123456789ABCDEF"


def parse_int_strict(text: str, line_no: int) -> Tuple[bool, int]:
    """
    Parses a line as an integer, reporting errors to the console.

    Accepts:
        - Optional leading + or -
        - Digits only after sign

    Rejects:
        - Empty lines
        - Floats (e.g., 12.3)
        - Scientific notation (e.g., 1e5)
        - Any non-digit characters (after optional sign)

    Args:
        text: Raw line (already stripped).
        line_no: Line number for error reporting.

    Returns:
        (success, value)
    """
    if not text:
        print(f"[ERROR] Line {line_no}: empty/blank line. Skipping.")
        return False, 0

    sign = 1
    start_idx = 0

    if text[0] == "+":
        start_idx = 1
    elif text[0] == "-":
        sign = -1
        start_idx = 1

    if start_idx == len(text):
        print(f"[ERROR] Line {line_no}: "
              "sign without digits '{text}'. Skipping.")
        return False, 0

    value = 0
    for ch in text[start_idx:]:
        if ch < "0" or ch > "9":
            print(f"[ERROR] Line {line_no}: "
                  "not an integer '{text}'. Skipping.")
            return False, 0
        value = value * 10 + (ord(ch) - ord("0"))

    return True, sign * value


def convert_positive_to_base(n: int, base: int, digits: str) -> str:
    """
    Converts a non-negative integer to a string in the given base using
    repeated division.

    Args:
        n: Non-negative integer.
        base: Target base (2 for binary, 16 for hex).
        digits: Digit table (e.g., "01" or HEX_DIGITS).

    Returns:
        The converted string (no prefix).
    """
    if n == 0:
        return "0"

    result_chars: List[str] = []
    value = n

    while value > 0:
        remainder = value % base
        result_chars.append(digits[remainder])
        value //= base

    result_chars.reverse()
    return "".join(result_chars)


def to_binary(n: int) -> str:
    """Converts an integer to binary string (no '0b' prefix)."""
    if n < 0:
        return "-" + convert_positive_to_base(-n, 2, "01")
    return convert_positive_to_base(n, 2, "01")


def to_hex(n: int) -> str:
    """Converts an integer to hexadecimal string (no '0x' prefix)."""
    if n < 0:
        return "-" + convert_positive_to_base(-n, 16, HEX_DIGITS)
    return convert_positive_to_base(n, 16, HEX_DIGITS)


def read_numbers(filepath: str) -> Tuple[List[int], int]:
    """
    Reads integers from a file (one per line), skipping invalid lines.

    Args:
        filepath: Input file path.

    Returns:
        (numbers, invalid_count)
    """
    numbers: List[int] = []
    invalid_count = 0

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line_no, raw_line in enumerate(file, start=1):
                line = raw_line.strip()
                ok, value = parse_int_strict(line, line_no)
                if ok:
                    numbers.append(value)
                else:
                    invalid_count += 1
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)
    except PermissionError:
        print(f"[ERROR] Permission denied: {filepath}")
        sys.exit(1)

    return numbers, invalid_count


def build_report(
    numbers: List[int],
    invalid_count: int,
    elapsed_seconds: float,
    console_limit: int | None = None,
) -> str:
    """
    Builds output report text.

    If console_limit is provided, only the first N conversions are included,
    and a note is appended indicating full results were written to file.
    """
    lines: List[str] = []
    lines.append("=== Conversion Results (Decimal -> Binary / Hex) ===")
    lines.append(f"Valid numbers: {len(numbers)}")
    lines.append(f"Invalid lines skipped: {invalid_count}")
    lines.append("")

    lines.append("Decimal -> Binary -> Hex")
    lines.append("------------------------")

    shown = numbers if console_limit is None else numbers[:console_limit]
    for n in shown:
        b = to_binary(n)
        h = to_hex(n)
        lines.append(f"{n} -> {b} -> {h}")

    if console_limit is not None and len(numbers) > console_limit:
        lines.append("")
        lines.append(
            f"... showing first {console_limit} of {len(numbers)} items. "
            f"Full results were written to {RESULTS_FILENAME}."
        )

    lines.append("")
    lines.append(f"Elapsed time (s): {elapsed_seconds:.6f}")

    return "\n".join(lines) + "\n"


def write_results(output_text: str, filename: str = RESULTS_FILENAME) -> None:
    """Writes the report text to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(output_text)


def main() -> None:
    """Program entry point."""
    start = time.perf_counter()

    if len(sys.argv) < 2:
        print("Usage: python3 convertNumbers.py fileWithData.txt")
        sys.exit(1)

    filepath = sys.argv[1]
    numbers, invalid_count = read_numbers(filepath)

    elapsed = time.perf_counter() - start

    report_full = build_report(
        numbers=numbers,
        invalid_count=invalid_count,
        elapsed_seconds=elapsed,
        console_limit=None,
    )
    report_console = build_report(
        numbers=numbers,
        invalid_count=invalid_count,
        elapsed_seconds=elapsed,
        console_limit=15,
    )

    print(report_console, end="")
    write_results(report_full)


if __name__ == "__main__":
    main()
