from __future__ import annotations

import math
import random
import statistics
from .formulas import (
    advanced_depletion_capacitance_f,
    advanced_inductance_h,
    advanced_oxide_capacitance_f,
    advanced_substrate_conductance_s,
    coupling_capacitance_f,
    depletion_capacitance_f,
    mutual_inductance_h,
    oxide_capacitance_f,
    substrate_conductance_s,
    substrate_resistance_ohm,
    tsv_inductance_h,
    tsv_resistance_ohm,
)
from .models import (
    ArrayResult,
    MonteCarloConfig,
    OperatingPoint,
    SingleTSVResult,
    SweepConfig,
    TSVGeometry,
    TSVProcess,
)


def extract_single_tsv(geometry: TSVGeometry, process: TSVProcess, op: OperatingPoint) -> SingleTSVResult:
    r_tsv = tsv_resistance_ohm(
        diameter_um=geometry.diameter_um,
        height_um=geometry.height_um,
        frequency_hz=op.frequency_hz,
        temperature_c=op.temperature_c,
        resistivity_ohm_m=process.metal_resistivity_ohm_m,
    )
    l_tsv = tsv_inductance_h(geometry.diameter_um, geometry.height_um)
    c_ox = oxide_capacitance_f(
        diameter_um=geometry.diameter_um,
        height_um=geometry.height_um,
        oxide_thickness_nm=geometry.oxide_thickness_nm,
        eps_ox_rel=process.eps_ox_rel,
    )
    c_dep = depletion_capacitance_f(
        diameter_um=geometry.diameter_um,
        height_um=geometry.height_um,
        oxide_thickness_nm=geometry.oxide_thickness_nm,
        substrate_doping_cm3=process.substrate_doping_cm3,
        bias_v=op.bias_v,
    )
    r_sub = substrate_resistance_ohm(
        diameter_um=geometry.diameter_um,
        height_um=geometry.height_um,
        substrate_resistivity_ohm_cm=process.substrate_resistivity_ohm_cm,
    )
    g_sub = substrate_conductance_s(r_sub)

    if op.model_level == "advanced":
        l_tsv = advanced_inductance_h(l_tsv, op.frequency_hz)
        c_ox = advanced_oxide_capacitance_f(c_ox, op.frequency_hz)
        c_dep = advanced_depletion_capacitance_f(c_dep, op.frequency_hz)
        g_sub = advanced_substrate_conductance_s(g_sub, op.frequency_hz)

    return SingleTSVResult(r_tsv_ohm=r_tsv, l_tsv_h=l_tsv, c_ox_f=c_ox, c_dep_f=c_dep, r_sub_ohm=r_sub, g_sub_s=g_sub)


def build_frequency_sweep(sweep: SweepConfig) -> list[float]:
    if sweep.points <= 0:
        raise ValueError("sweep points must be positive")
    if sweep.f_start_hz <= 0.0 or sweep.f_stop_hz <= 0.0:
        raise ValueError("sweep frequencies must be positive")

    if sweep.points == 1:
        return [sweep.f_start_hz]

    if sweep.spacing == "lin":
        step = (sweep.f_stop_hz - sweep.f_start_hz) / (sweep.points - 1)
        return [sweep.f_start_hz + i * step for i in range(sweep.points)]

    if sweep.spacing != "log":
        raise ValueError("spacing must be 'lin' or 'log'")

    ratio = (sweep.f_stop_hz / sweep.f_start_hz) ** (1.0 / (sweep.points - 1))
    return [sweep.f_start_hz * (ratio**i) for i in range(sweep.points)]


def extract_sweep_tsv(
    geometry: TSVGeometry,
    process: TSVProcess,
    op: OperatingPoint,
    sweep: SweepConfig,
) -> dict[str, list[float] | str]:
    freqs = build_frequency_sweep(sweep)
    out: dict[str, list[float] | str] = {
        "model_level": op.model_level,
        "frequency_hz": freqs,
        "r_tsv_ohm": [],
        "l_tsv_h": [],
        "c_ox_f": [],
        "c_dep_f": [],
        "r_sub_ohm": [],
        "g_sub_s": [],
    }

    for f in freqs:
        pt = OperatingPoint(
            frequency_hz=f,
            temperature_c=op.temperature_c,
            bias_v=op.bias_v,
            model_level=op.model_level,
        )
        single = extract_single_tsv(geometry, process, pt)
        out["r_tsv_ohm"].append(single.r_tsv_ohm)
        out["l_tsv_h"].append(single.l_tsv_h)
        out["c_ox_f"].append(single.c_ox_f)
        out["c_dep_f"].append(single.c_dep_f)
        out["r_sub_ohm"].append(single.r_sub_ohm)
        out["g_sub_s"].append(single.g_sub_s)

    return out


def _grid_positions(rows: int, cols: int, pitch_um: float) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for r in range(rows):
        for c in range(cols):
            pts.append((c * pitch_um, r * pitch_um))
    return pts


def extract_tsv_array(
    geometry: TSVGeometry,
    process: TSVProcess,
    op: OperatingPoint,
    rows: int,
    cols: int,
    pitch_um: float | None = None,
) -> ArrayResult:
    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be positive")
    p = pitch_um if pitch_um is not None else geometry.pitch_um
    if p is None or p <= 0:
        raise ValueError("pitch_um must be provided and positive")

    base = extract_single_tsv(geometry, process, op)
    pts = _grid_positions(rows, cols, p)
    n = len(pts)

    mtx_l = [[0.0 for _ in range(n)] for _ in range(n)]
    mtx_c = [[0.0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        xi, yi = pts[i]
        for j in range(i + 1, n):
            xj, yj = pts[j]
            dist = math.hypot(xi - xj, yi - yj)
            mij = mutual_inductance_h(dist, geometry.height_um)
            cij = coupling_capacitance_f(dist, geometry.height_um, process.eps_si_rel)
            mtx_l[i][j] = mtx_l[j][i] = mij
            mtx_c[i][j] = mtx_c[j][i] = cij

    return ArrayResult(single=base, mutual_l_h=mtx_l, coupling_c_f=mtx_c)


def _safe_gauss(rng: random.Random, nominal: float, sigma: float, floor: float = 1e-30) -> float:
    if sigma <= 0.0:
        return nominal
    return max(rng.gauss(nominal, sigma), floor)


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    if len(values) == 1:
        return values[0]

    sorted_vals = sorted(values)
    pos = q * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_vals[lo]
    weight = pos - lo
    return sorted_vals[lo] * (1.0 - weight) + sorted_vals[hi] * weight


def _series_stats(values: list[float]) -> dict[str, float]:
    std = statistics.stdev(values) if len(values) > 1 else 0.0
    return {
        "mean": statistics.mean(values),
        "std": std,
        "p5": _percentile(values, 0.05),
        "p50": _percentile(values, 0.50),
        "p95": _percentile(values, 0.95),
    }


def run_monte_carlo_tsv(
    geometry: TSVGeometry,
    process: TSVProcess,
    op: OperatingPoint,
    mc: MonteCarloConfig,
) -> dict[str, object]:
    if mc.mc_samples <= 0:
        raise ValueError("mc_samples must be positive")

    rng = random.Random(mc.seed)
    metrics: dict[str, list[float]] = {
        "r_tsv_ohm": [],
        "l_tsv_h": [],
        "c_ox_f": [],
        "c_dep_f": [],
    }

    for _ in range(mc.mc_samples):
        perturbed_geometry = TSVGeometry(
            diameter_um=_safe_gauss(rng, geometry.diameter_um, mc.sigma_diameter_um),
            height_um=geometry.height_um,
            oxide_thickness_nm=_safe_gauss(rng, geometry.oxide_thickness_nm, mc.sigma_oxide_thickness_nm),
            pitch_um=geometry.pitch_um,
        )
        perturbed_process = TSVProcess(
            metal_resistivity_ohm_m=_safe_gauss(rng, process.metal_resistivity_ohm_m, mc.sigma_metal_resistivity_ohm_m),
            substrate_resistivity_ohm_cm=_safe_gauss(
                rng,
                process.substrate_resistivity_ohm_cm,
                mc.sigma_substrate_resistivity_ohm_cm,
            ),
            substrate_doping_cm3=process.substrate_doping_cm3,
            eps_ox_rel=process.eps_ox_rel,
            eps_si_rel=process.eps_si_rel,
        )
        perturbed_op = OperatingPoint(
            frequency_hz=op.frequency_hz,
            temperature_c=op.temperature_c + rng.gauss(0.0, mc.sigma_temperature_c),
            bias_v=op.bias_v,
            model_level=op.model_level,
        )
        out = extract_single_tsv(perturbed_geometry, perturbed_process, perturbed_op)
        metrics["r_tsv_ohm"].append(out.r_tsv_ohm)
        metrics["l_tsv_h"].append(out.l_tsv_h)
        metrics["c_ox_f"].append(out.c_ox_f)
        metrics["c_dep_f"].append(out.c_dep_f)

    return {
        "samples": mc.mc_samples,
        "seed": mc.seed,
        "model_level": op.model_level,
        "statistics": {name: _series_stats(values) for name, values in metrics.items()},
    }
