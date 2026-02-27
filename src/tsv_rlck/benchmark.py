from __future__ import annotations

from dataclasses import asdict

from .extractor import extract_single_tsv
from .models import OperatingPoint, TSVGeometry, TSVProcess


def compare_single_against_reference(
    geometry: TSVGeometry,
    process: TSVProcess,
    op: OperatingPoint,
    reference: dict[str, float],
) -> dict[str, dict[str, float]]:
    result = extract_single_tsv(geometry, process, op)
    actual = asdict(result)
    report: dict[str, dict[str, float]] = {}
    for key, ref_value in reference.items():
        got = actual[key]
        abs_err = got - ref_value
        rel_err_pct = 0.0 if ref_value == 0 else abs_err / ref_value * 100.0
        report[key] = {
            "actual": got,
            "reference": ref_value,
            "abs_error": abs_err,
            "rel_error_pct": rel_err_pct,
        }
    return report


def summarize_error(report: dict[str, dict[str, float]]) -> dict[str, float]:
    abs_vals = [abs(v["abs_error"]) for v in report.values()]
    rel_vals = [abs(v["rel_error_pct"]) for v in report.values()]
    n = len(abs_vals)
    if n == 0:
        return {"mae": 0.0, "mape_pct": 0.0, "max_abs_error": 0.0, "max_rel_error_pct": 0.0}
    return {
        "mae": sum(abs_vals) / n,
        "mape_pct": sum(rel_vals) / n,
        "max_abs_error": max(abs_vals),
        "max_rel_error_pct": max(rel_vals),
    }
