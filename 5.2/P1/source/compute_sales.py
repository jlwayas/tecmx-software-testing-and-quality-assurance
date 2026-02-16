"""
computeSales.py

Usage:
    python computeSales.py priceCatalogue.json salesRecord.json

Catalogue format (TC*):
- A JSON list of objects with keys: "title" and "price" (plus other fields)

Sales format (TC*):
- A JSON list of objects with keys:
    "SALE_ID", "Product", "Quantity" (plus other fields)

Behavior:
- Quantity < 0 is VALID and will subtract from the total
    (returns/cancellations)
- Quantity = 0 is ignored (warning) to avoid meaningless rows
- Invalid rows are reported and execution continues

Outputs:
- Console
- SalesResults.txt
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

RESULTS_FILENAME = "SalesResults.txt"


@dataclass(frozen=True)
class Totals:
    """Aggregated totals and counters for the report."""
    net_total: float
    processed_rows: int
    positive_total: float
    negative_total: float


def _print_error(msg: str) -> None:
    """Print error/warning messages to stderr."""
    print(f"[ERROR] {msg}", file=sys.stderr)


def _read_json(path: Path, errors: List[str]) -> Optional[Any]:
    """Safely read a JSON file; return decoded object or None on failure."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        errors.append(f"File not found: {path}")
        _print_error(errors[-1])
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in file {path}: {exc}")
        _print_error(errors[-1])
    except OSError as exc:
        errors.append(f"OS error reading file {path}: {exc}")
        _print_error(errors[-1])
    return None


def _to_float(value: Any) -> Optional[float]:
    """Convert value to float if possible; otherwise return None."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def build_price_map(catalogue_raw: Any, errors: List[str]) -> Dict[str, float]:
    """
    Normalize catalogue into {title: price}.
    Catalogue must be a list of dict entries with "title" and "price".
    """
    price_map: Dict[str, float] = {}

    if not isinstance(catalogue_raw, list):
        errors.append("Catalogue must be a JSON list (array).")
        _print_error(errors[-1])
        return price_map

    for idx, entry in enumerate(catalogue_raw):
        if not isinstance(entry, dict):
            errors.append(f"Catalogue entry #{idx} is not an object: {entry}")
            _print_error(errors[-1])
            continue

        title = entry.get("title")
        price = _to_float(entry.get("price"))

        if not isinstance(title, str) or not title.strip():
            errors.append(f"Catalogue entry #{idx} "
                          "missing valid 'title': {entry}")
            _print_error(errors[-1])
            continue

        # Negative prices treated as invalid catalogue data
        if price is None or price < 0:
            errors.append(f"Invalid price for '{title}': {entry.get('price')}")
            _print_error(errors[-1])
            continue

        price_map[title] = price

    return price_map


def compute_total_from_rows(
    price_map: Dict[str, float],
    sales_raw: Any,
    errors: List[str],
) -> Totals:
    """
    Compute totals from sales rows:
    - Each row should contain "Product" and "Quantity"
    - Quantity < 0 is valid and subtracts (returns/cancellations)

    Returns:
        Totals: net_total, processed_rows, positive_total, negative_total
    """
    if not isinstance(sales_raw, list):
        errors.append("Sales record must be a JSON list (array).")
        _print_error(errors[-1])
        return Totals(
            net_total=0.0,
            processed_rows=0,
            positive_total=0.0,
            negative_total=0.0,
        )

    net_total = 0.0
    positive_total = 0.0
    negative_total = 0.0
    processed_rows = 0

    for idx, row in enumerate(sales_raw):
        if not isinstance(row, dict):
            errors.append(f"Sales row #{idx} is not an object: {row}")
            _print_error(errors[-1])
            continue

        product = row.get("Product")
        if not isinstance(product, str) or not product.strip():
            errors.append(f"Sales row #{idx} missing valid 'Product': {row}")
            _print_error(errors[-1])
            continue

        qty = _to_float(row.get("Quantity"))
        if qty is None:
            errors.append(
                f"Sales row #{idx} invalid 'Quantity' for "
                "'{product}': {row.get('Quantity')}"
            )
            _print_error(errors[-1])
            continue

        if qty == 0:
            errors.append(f"Sales row #{idx} zero 'Quantity' for "
                          "'{product}'. Skipping.")
            _print_error(errors[-1])
            continue

        if qty < 0:
            # Valid: treat as return/cancellation
            errors.append(
                f"Sales row #{idx} negative 'Quantity' for '{product}' "
                f"(valid return/cancellation): {qty}"
            )
            _print_error(errors[-1])

        price = price_map.get(product)
        if price is None:
            errors.append(f"Sales row #{idx}: product not in catalogue "
                          "'{product}'. Skipping.")
            _print_error(errors[-1])
            continue

        line_total = price * qty
        net_total += line_total
        processed_rows += 1

        if line_total >= 0:
            positive_total += line_total
        else:
            negative_total += line_total  # negative value

    return Totals(
        net_total=net_total,
        processed_rows=processed_rows,
        positive_total=positive_total,
        negative_total=negative_total,
    )


def build_report(totals: Totals, elapsed: float, errors: List[str]) -> str:
    """Create a human-readable report."""
    lines: List[str] = []
    lines.append("Sales Computation Results")
    lines.append("=" * 28)
    lines.append(f"Processed rows:   {totals.processed_rows}")
    lines.append(f"Sales subtotal:   {totals.positive_total:,.2f}")
    lines.append(f"Returns subtotal: {totals.negative_total:,.2f}")
    lines.append(f"Net total cost:   {totals.net_total:,.2f}")
    lines.append(f"Elapsed time:     {elapsed:.6f} seconds")
    lines.append("")

    if errors:
        lines.append("Warnings / Errors (execution continued):")
        lines.append("-" * 38)
        for err in errors:
            lines.append(f"- {err}")
        lines.append("")
    else:
        lines.append("No errors detected.")
        lines.append("")

    return "\n".join(lines)


def write_results(report: str, errors: List[str]) -> None:
    """Write report to SalesResults.txt."""
    try:
        with open(RESULTS_FILENAME, "w", encoding="utf-8") as file:
            file.write(report)
    except OSError as exc:
        errors.append(f"Could not write {RESULTS_FILENAME}: {exc}")
        _print_error(errors[-1])


def main(argv: List[str]) -> int:
    """Program entry point."""
    errors: List[str] = []

    if len(argv) < 3:
        _print_error("Usage: python computeSales.py "
                     "priceCatalogue.json salesRecord.json")
        return 2

    catalogue_path = Path(argv[1])
    sales_path = Path(argv[2])

    start = time.perf_counter()

    catalogue_raw = _read_json(catalogue_path, errors)
    sales_raw = _read_json(sales_path, errors)

    if catalogue_raw is None or sales_raw is None:
        elapsed = time.perf_counter() - start
        totals = Totals(
            net_total=0.0,
            processed_rows=0,
            positive_total=0.0,
            negative_total=0.0,
        )
        report = build_report(totals, elapsed, errors)
        print(report)
        write_results(report, errors)
        return 1

    price_map = build_price_map(catalogue_raw, errors)
    totals = compute_total_from_rows(price_map, sales_raw, errors)

    elapsed = time.perf_counter() - start
    report = build_report(totals, elapsed, errors)

    print(report)
    write_results(report, errors)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
