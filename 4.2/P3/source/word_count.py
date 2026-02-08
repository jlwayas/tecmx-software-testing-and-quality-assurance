"""
wordCount.py

Reads a text file and computes the frequency of each distinct word.

Requirements:
- Invoked from the command line with the input file path as a parameter.
- Identifies all distinct words and their frequencies.
- Prints results to the console and writes them to WordCountResults.txt.
- Handles invalid data gracefully (reports issues and continues).
- Uses basic algorithms only (no specialized counting libraries like Counter).
- Measures elapsed time (read + compute) and reports it in console and file.
- PEP8 compliant.
"""


from __future__ import annotations

import sys
import time
from typing import Dict, List, Tuple


RESULTS_FILENAME = "WordCountResults.txt"


def normalize_word(token: str) -> str:
    """
    Normalizes a token into a 'word'.

    This keeps only alphanumeric characters and apostrophes,
    and converts to lowercase.

    Examples:
        "Hello," -> "hello"
        "can't"  -> "can't"
        "C++"    -> "c"
        "..."    -> ""

    Args:
        token: Raw token from splitting.

    Returns:
        Normalized word (possibly empty).
    """
    cleaned_chars: List[str] = []
    for ch in token:
        if ch.isalnum() or ch == "'":
            cleaned_chars.append(ch.lower())

    return "".join(cleaned_chars)


def read_and_count_words(filepath: str) -> Tuple[Dict[str, int], int, int]:
    """
    Reads the file and counts word frequencies.

    Invalid data handling:
    - Empty/blank lines are reported and skipped.
    - Tokens that become empty after normalization are reported and skipped.

    Args:
        filepath: Input file path.

    Returns:
        (frequency_map, total_words_counted, invalid_items_count)
    """
    freq: Dict[str, int] = {}
    total_words = 0
    invalid_items = 0

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line_no, raw_line in enumerate(file, start=1):
                line = raw_line.strip()

                if not line:
                    invalid_items += 1
                    print(f"[ERROR] Line {line_no}: "
                          "empty/blank line. Skipping.")
                    continue

                tokens = line.split()
                for token in tokens:
                    word = normalize_word(token)

                    if not word:
                        invalid_items += 1
                        print(
                            f"[ERROR] Line {line_no}: "
                            "invalid token '{token}'. "
                            "Skipping."
                        )
                        continue

                    freq[word] = freq.get(word, 0) + 1
                    total_words += 1
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)
    except PermissionError:
        print(f"[ERROR] Permission denied: {filepath}")
        sys.exit(1)

    return freq, total_words, invalid_items


def format_results(
    freq: Dict[str, int],
    total_words: int,
    distinct_words: int,
    invalid_items: int,
    elapsed_seconds: float,
) -> str:
    """
    Builds the final report text.

    Words are sorted by:
    1) highest frequency (descending)
    2) alphabetically (ascending)
    """
    lines: List[str] = []
    lines.append("=== Word Count Results ===")
    lines.append(f"Total valid words counted: {total_words}")
    lines.append(f"Distinct words: {distinct_words}")
    lines.append(f"Invalid items skipped: {invalid_items}")
    lines.append("")

    items = list(freq.items())
    items.sort(key=lambda item: (-item[1], item[0]))

    lines.append("Word -> Frequency")
    lines.append("-----------------")
    for word, count in items:
        lines.append(f"{word} -> {count}")

    lines.append("")
    lines.append(f"Elapsed time (s): {elapsed_seconds:.6f}")

    return "\n".join(lines) + "\n"


def write_results(output_text: str, filename: str = RESULTS_FILENAME) -> None:
    """Writes the output report to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(output_text)


def main() -> None:
    """Program entry point."""
    start = time.perf_counter()

    if len(sys.argv) < 2:
        print("Usage: python3 wordCount.py fileWithData.txt")
        sys.exit(1)

    filepath = sys.argv[1]
    freq, total_words, invalid_items = read_and_count_words(filepath)

    elapsed = time.perf_counter() - start
    distinct_words = len(freq)

    output = format_results(
        freq=freq,
        total_words=total_words,
        distinct_words=distinct_words,
        invalid_items=invalid_items,
        elapsed_seconds=elapsed,
    )

    print(type(output), end="")
    write_results(output)


if __name__ == "__main__":
    main()
