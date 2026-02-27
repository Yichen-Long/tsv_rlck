from __future__ import annotations

import math
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
        return {
            "mae": 0.0,
            "mape_pct": 0.0,
            "rmse": 0.0,
            "max_abs_error": 0.0,
            "max_rel_error_pct": 0.0,
        }
    rmse = math.sqrt(sum(v * v for v in abs_vals) / n)
    return {
        "mae": sum(abs_vals) / n,
        "mape_pct": sum(rel_vals) / n,
        "rmse": rmse,
        "max_abs_error": max(abs_vals),
        "max_rel_error_pct": max(rel_vals),
    }


def compare_batch_against_reference(
    cases: list[dict[str, object]],
    default_model_level: str = "simple",
) -> dict[str, object]:
    details: list[dict[str, object]] = []
    per_case_mae: list[float] = []
    per_case_mape: list[float] = []
    per_case_rmse: list[float] = []
    per_case_max_abs: list[float] = []
    per_case_max_rel: list[float] = []

    for idx, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError("each benchmark case must be an object")

        input_data = case.get("input")
        reference = case.get("reference")
        if not isinstance(input_data, dict) or not isinstance(reference, dict):
            raise ValueError("each benchmark case requires input and reference objects")

        g = input_data.get("geometry") if isinstance(input_data.get("geometry"), dict) else {}
        p = input_data.get("process") if isinstance(input_data.get("process"), dict) else {}
        o = input_data.get("operating_point") if isinstance(input_data.get("operating_point"), dict) else {}

        geometry = TSVGeometry(
            diameter_um=float(g["diameter_um"]),
            height_um=float(g["height_um"]),
            oxide_thickness_nm=float(g["oxide_thickness_nm"]),
            pitch_um=g.get("pitch_um"),
        )
        process = TSVProcess(
            metal_resistivity_ohm_m=float(p.get("metal_resistivity_ohm_m", TSVProcess().metal_resistivity_ohm_m)),
            substrate_resistivity_ohm_cm=float(
                p.get("substrate_resistivity_ohm_cm", TSVProcess().substrate_resistivity_ohm_cm)
            ),
            substrate_doping_cm3=float(p.get("substrate_doping_cm3", TSVProcess().substrate_doping_cm3)),
            eps_ox_rel=float(p.get("eps_ox_rel", TSVProcess().eps_ox_rel)),
            eps_si_rel=float(p.get("eps_si_rel", TSVProcess().eps_si_rel)),
        )
        op = OperatingPoint(
            frequency_hz=float(o["frequency_hz"]),
            temperature_c=float(o.get("temperature_c", 25.0)),
            bias_v=float(o.get("bias_v", 0.0)),
            model_level=str(o.get("model_level", default_model_level)),
        )

        detail = compare_single_against_reference(geometry, process, op, reference)
        summary = summarize_error(detail)

        per_case_mae.append(summary["mae"])
        per_case_mape.append(summary["mape_pct"])
        per_case_rmse.append(summary["rmse"])
        per_case_max_abs.append(summary["max_abs_error"])
        per_case_max_rel.append(summary["max_rel_error_pct"])

        details.append(
            {
                "name": str(case.get("name", f"case_{idx}")),
                "model_level": op.model_level,
                "details": detail,
                "summary": summary,
            }
        )

    n = len(details)
    if n == 0:
        overall = {
            "cases": 0,
            "mean_mae": 0.0,
            "mean_mape_pct": 0.0,
            "mean_rmse": 0.0,
            "worst_max_abs_error": 0.0,
            "worst_max_rel_error_pct": 0.0,
        }
    else:
        overall = {
            "cases": n,
            "mean_mae": sum(per_case_mae) / n,
            "mean_mape_pct": sum(per_case_mape) / n,
            "mean_rmse": sum(per_case_rmse) / n,
            "worst_max_abs_error": max(per_case_max_abs),
            "worst_max_rel_error_pct": max(per_case_max_rel),
        }

    return {
        "cases": details,
        "overall": overall,
    }
