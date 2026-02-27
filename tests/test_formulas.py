import math
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tsv_rlck.extractor import build_frequency_sweep, extract_single_tsv
from tsv_rlck.formulas import (
    coupling_capacitance_f,
    mutual_inductance_h,
    oxide_capacitance_f,
    tsv_inductance_h,
    tsv_resistance_ohm,
)
from tsv_rlck.models import OperatingPoint, SweepConfig, TSVGeometry, TSVProcess


class FormulaTests(unittest.TestCase):
    def test_positive_single_terms(self) -> None:
        r = tsv_resistance_ohm(10.0, 60.0, 1e9, 25.0, 1.68e-8)
        l = tsv_inductance_h(10.0, 60.0)
        cox = oxide_capacitance_f(10.0, 60.0, 200.0, 3.9)

        self.assertGreater(r, 0.0)
        self.assertGreater(l, 0.0)
        self.assertGreater(cox, 0.0)

    def test_coupling_decreases_with_distance(self) -> None:
        m1 = mutual_inductance_h(20.0, 60.0)
        m2 = mutual_inductance_h(40.0, 60.0)
        c1 = coupling_capacitance_f(20.0, 60.0, 11.7)
        c2 = coupling_capacitance_f(40.0, 60.0, 11.7)

        self.assertGreater(m1, m2)
        self.assertGreater(c1, c2)

    def test_linear_sweep_boundaries_and_count(self) -> None:
        sweep = SweepConfig(f_start_hz=1e6, f_stop_hz=1e9, points=5, spacing="lin")
        freqs = build_frequency_sweep(sweep)
        self.assertEqual(len(freqs), 5)
        self.assertAlmostEqual(freqs[0], 1e6)
        self.assertAlmostEqual(freqs[-1], 1e9)

    def test_log_sweep_ratios_constant(self) -> None:
        sweep = SweepConfig(f_start_hz=1e6, f_stop_hz=1e9, points=4, spacing="log")
        freqs = build_frequency_sweep(sweep)
        ratios = [freqs[i + 1] / freqs[i] for i in range(len(freqs) - 1)]
        self.assertTrue(all(math.isclose(ratios[0], r, rel_tol=1e-12) for r in ratios[1:]))

    def test_advanced_model_has_frequency_variation(self) -> None:
        g = TSVGeometry(diameter_um=10.0, height_um=60.0, oxide_thickness_nm=200.0)
        p = TSVProcess()
        op_low = OperatingPoint(frequency_hz=1e6, model_level="advanced")
        op_high = OperatingPoint(frequency_hz=1e10, model_level="advanced")

        low = extract_single_tsv(g, p, op_low)
        high = extract_single_tsv(g, p, op_high)

        self.assertNotEqual(low.l_tsv_h, high.l_tsv_h)
        self.assertNotEqual(low.c_ox_f, high.c_ox_f)
        self.assertNotEqual(low.c_dep_f, high.c_dep_f)
        self.assertNotEqual(low.g_sub_s, high.g_sub_s)


if __name__ == "__main__":
    unittest.main()
