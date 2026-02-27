from __future__ import annotations

from .models import OperatingPoint, SingleTSVResult


def to_spice_subckt(result: SingleTSVResult, op: OperatingPoint, name: str = "TSV_RLCK") -> str:
    lines = [
        f"* Analytical TSV RLCK model @ f={op.frequency_hz:.6g}Hz T={op.temperature_c:.2f}C Vb={op.bias_v:.3f}V",
        f".subckt {name} p n sub",
        f"RTSV p x {result.r_tsv_ohm:.6e}",
        f"LTSV x n {result.l_tsv_h:.6e}",
        f"COX x sub {result.c_ox_f:.6e}",
        f"CDEP x sub {result.c_dep_f:.6e}",
        f"RSUB sub 0 {result.r_sub_ohm:.6e}",
        f"GSUB sub 0 value={{V(sub,0)*{result.g_sub_s:.6e}}}",
        ".ends",
    ]
    return "\n".join(lines) + "\n"
