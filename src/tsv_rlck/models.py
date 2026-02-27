from dataclasses import dataclass, field
from typing import List, Literal


@dataclass(slots=True)
class TSVGeometry:
    diameter_um: float
    height_um: float
    oxide_thickness_nm: float
    pitch_um: float | None = None


@dataclass(slots=True)
class TSVProcess:
    metal_resistivity_ohm_m: float = 1.68e-8
    substrate_resistivity_ohm_cm: float = 10.0
    substrate_doping_cm3: float = 1.0e15
    eps_ox_rel: float = 3.9
    eps_si_rel: float = 11.7


@dataclass(slots=True)
class OperatingPoint:
    frequency_hz: float
    temperature_c: float = 25.0
    bias_v: float = 0.0
    model_level: Literal["simple", "advanced"] = "simple"


@dataclass(slots=True)
class SweepConfig:
    f_start_hz: float
    f_stop_hz: float
    points: int
    spacing: Literal["lin", "log"] = "lin"


@dataclass(slots=True)
class MonteCarloConfig:
    mc_samples: int
    seed: int | None = None
    sigma_diameter_um: float = 0.0
    sigma_oxide_thickness_nm: float = 0.0
    sigma_metal_resistivity_ohm_m: float = 0.0
    sigma_substrate_resistivity_ohm_cm: float = 0.0
    sigma_temperature_c: float = 0.0


@dataclass(slots=True)
class SingleTSVResult:
    r_tsv_ohm: float
    l_tsv_h: float
    c_ox_f: float
    c_dep_f: float
    r_sub_ohm: float
    g_sub_s: float


@dataclass(slots=True)
class ArrayResult:
    single: SingleTSVResult
    mutual_l_h: List[List[float]] = field(default_factory=list)
    coupling_c_f: List[List[float]] = field(default_factory=list)
    node_order: List[str] = field(default_factory=list)
    node_roles: List[str] = field(default_factory=list)
