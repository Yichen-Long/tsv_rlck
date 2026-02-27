from __future__ import annotations

import math

EPS0 = 8.854187817e-12
MU0 = 4.0 * math.pi * 1e-7
Q = 1.602176634e-19
EPS_SI_ABS = 11.7 * EPS0
K_B = 1.380649e-23
T0_K = 293.15
ALPHA_CU = 0.0039


def _um_to_m(v_um: float) -> float:
    return v_um * 1e-6


def _nm_to_m(v_nm: float) -> float:
    return v_nm * 1e-9


def _safe_positive(v: float, floor: float = 1e-30) -> float:
    return v if v > floor else floor


def tsv_resistance_ohm(
    diameter_um: float,
    height_um: float,
    frequency_hz: float,
    temperature_c: float,
    resistivity_ohm_m: float,
) -> float:
    d = _um_to_m(diameter_um)
    h = _um_to_m(height_um)
    a = d / 2.0
    area_dc = math.pi * a * a
    temp_ratio = 1.0 + ALPHA_CU * ((temperature_c + 273.15) - T0_K)
    rho_t = resistivity_ohm_m * temp_ratio

    r_dc = rho_t * h / _safe_positive(area_dc)

    omega = 2.0 * math.pi * max(frequency_hz, 0.0)
    if omega <= 0.0:
        return r_dc

    delta = math.sqrt(2.0 * rho_t / _safe_positive(omega * MU0))
    if delta >= a:
        return r_dc

    area_skin = math.pi * (a * a - (a - delta) * (a - delta))
    return rho_t * h / _safe_positive(area_skin)


def tsv_inductance_h(diameter_um: float, height_um: float) -> float:
    d = _um_to_m(diameter_um)
    h = _um_to_m(height_um)
    ratio = _safe_positive(4.0 * h / _safe_positive(d))
    return MU0 * h / (2.0 * math.pi) * (math.log(ratio) + 0.25)


def oxide_capacitance_f(
    diameter_um: float,
    height_um: float,
    oxide_thickness_nm: float,
    eps_ox_rel: float,
) -> float:
    r1 = _um_to_m(diameter_um) / 2.0
    t_ox = _nm_to_m(oxide_thickness_nm)
    r2 = r1 + t_ox
    eps_ox = eps_ox_rel * EPS0
    h = _um_to_m(height_um)
    return 2.0 * math.pi * eps_ox * h / _safe_positive(math.log(r2 / _safe_positive(r1)))


def depletion_capacitance_f(
    diameter_um: float,
    height_um: float,
    oxide_thickness_nm: float,
    substrate_doping_cm3: float,
    bias_v: float,
) -> float:
    r1 = _um_to_m(diameter_um) / 2.0 + _nm_to_m(oxide_thickness_nm)
    na_m3 = max(substrate_doping_cm3, 1e10) * 1e6
    phi = 0.6
    v_eff = max(phi + bias_v, 1e-3)
    w_dep = math.sqrt(2.0 * EPS_SI_ABS * v_eff / _safe_positive(Q * na_m3))
    r2 = r1 + w_dep
    h = _um_to_m(height_um)
    return 2.0 * math.pi * EPS_SI_ABS * h / _safe_positive(math.log(r2 / _safe_positive(r1)))


def substrate_resistance_ohm(
    diameter_um: float,
    height_um: float,
    substrate_resistivity_ohm_cm: float,
) -> float:
    rho = substrate_resistivity_ohm_cm * 1e-2
    d = _um_to_m(diameter_um)
    h = _um_to_m(height_um)
    return rho * h / _safe_positive(math.pi * (d / 2.0) ** 2)


def substrate_conductance_s(r_sub_ohm: float) -> float:
    return 1.0 / _safe_positive(r_sub_ohm)


def mutual_inductance_h(distance_um: float, height_um: float) -> float:
    dist = _um_to_m(distance_um)
    h = _um_to_m(height_um)
    if dist <= 0:
        return 0.0
    return MU0 * h / (2.0 * math.pi) * math.log(1.0 + h / dist)


def coupling_capacitance_f(distance_um: float, height_um: float, eps_si_rel: float) -> float:
    dist = _um_to_m(distance_um)
    h = _um_to_m(height_um)
    eps = eps_si_rel * EPS0
    if dist <= 0:
        return 0.0
    return eps * h / dist
