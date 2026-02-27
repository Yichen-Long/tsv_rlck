from __future__ import annotations

import cmath
from .extractor import build_frequency_sweep, extract_single_tsv, extract_tsv_array
from .models import OperatingPoint, SingleTSVResult, SweepConfig, TSVGeometry, TSVProcess


def _abcd_series(z: complex) -> tuple[complex, complex, complex, complex]:
    return 1.0 + 0j, z, 0.0 + 0j, 1.0 + 0j


def _abcd_shunt(y: complex) -> tuple[complex, complex, complex, complex]:
    return 1.0 + 0j, 0.0 + 0j, y, 1.0 + 0j


def _abcd_mul(
    m1: tuple[complex, complex, complex, complex],
    m2: tuple[complex, complex, complex, complex],
) -> tuple[complex, complex, complex, complex]:
    a1, b1, c1, d1 = m1
    a2, b2, c2, d2 = m2
    return (
        a1 * a2 + b1 * c2,
        a1 * b2 + b1 * d2,
        c1 * a2 + d1 * c2,
        c1 * b2 + d1 * d2,
    )


def _rlck_to_abcd(result: SingleTSVResult, omega: float) -> tuple[complex, complex, complex, complex]:
    z_series = complex(result.r_tsv_ohm, omega * result.l_tsv_h)
    y_shunt_total = complex(result.g_sub_s + (1.0 / result.r_sub_ohm), omega * (result.c_ox_f + result.c_dep_f))
    y_half = y_shunt_total / 2.0

    m = _abcd_shunt(y_half)
    m = _abcd_mul(m, _abcd_series(z_series))
    m = _abcd_mul(m, _abcd_shunt(y_half))
    return m


def _abcd_to_s(
    abcd: tuple[complex, complex, complex, complex],
    z0: float,
) -> tuple[complex, complex, complex, complex]:
    a, b, c, d = abcd
    z0c = complex(z0, 0.0)
    denom = a + b / z0c + c * z0c + d

    s11 = (a + b / z0c - c * z0c - d) / denom
    s21 = 2.0 / denom
    s12 = 2.0 * (a * d - b * c) / denom
    s22 = (-a + b / z0c - c * z0c + d) / denom
    return s11, s21, s12, s22


def extract_sparams(
    geometry: TSVGeometry,
    process: TSVProcess,
    op: OperatingPoint,
    sweep: SweepConfig | None = None,
    z0: float = 50.0,
    rows: int = 1,
    cols: int = 1,
    pitch_um: float | None = None,
    topology: str = "grid",
) -> dict[str, object]:
    freqs = build_frequency_sweep(sweep) if sweep is not None else [op.frequency_hz]
    points: list[dict[str, float]] = []

    node_order: list[str] = ["N0"]
    node_roles: list[str] = ["S"]
    if rows * cols > 1:
        arr = extract_tsv_array(
            geometry,
            process,
            op,
            rows=rows,
            cols=cols,
            pitch_um=pitch_um,
            topology=topology,
        )
        node_order = arr.node_order
        node_roles = arr.node_roles

    for f in freqs:
        pt = OperatingPoint(
            frequency_hz=f,
            temperature_c=op.temperature_c,
            bias_v=op.bias_v,
            model_level=op.model_level,
        )
        single = extract_single_tsv(geometry, process, pt)
        omega = 2.0 * 3.141592653589793 * f
        s11, s21, s12, s22 = _abcd_to_s(_rlck_to_abcd(single, omega), z0)
        points.append(
            {
                "frequency_hz": f,
                "s11_re": s11.real,
                "s11_im": s11.imag,
                "s21_re": s21.real,
                "s21_im": s21.imag,
                "s12_re": s12.real,
                "s12_im": s12.imag,
                "s22_re": s22.real,
                "s22_im": s22.imag,
            }
        )

    return {
        "z0_ohm": z0,
        "model_level": op.model_level,
        "topology": topology,
        "node_order": node_order,
        "node_roles": node_roles,
        "points": points,
    }


def to_touchstone_s2p(sparams: dict[str, object]) -> str:
    z0 = float(sparams["z0_ohm"])
    points = sparams["points"]
    lines = ["# Hz S RI R {:.6g}".format(z0)]
    for p in points:
        lines.append(
            "{:.9e} {:.9e} {:.9e} {:.9e} {:.9e} {:.9e} {:.9e} {:.9e} {:.9e}".format(
                p["frequency_hz"],
                p["s11_re"],
                p["s11_im"],
                p["s21_re"],
                p["s21_im"],
                p["s12_re"],
                p["s12_im"],
                p["s22_re"],
                p["s22_im"],
            )
        )
    return "\n".join(lines) + "\n"
