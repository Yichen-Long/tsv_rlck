import math
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tsv_rlck.extractor import run_monte_carlo_tsv
from tsv_rlck.models import MonteCarloConfig, OperatingPoint, TSVGeometry, TSVProcess


class MonteCarloTests(unittest.TestCase):
    def test_monte_carlo_statistics_are_finite(self) -> None:
        geometry = TSVGeometry(diameter_um=10.0, height_um=60.0, oxide_thickness_nm=200.0)
        process = TSVProcess()
        op = OperatingPoint(frequency_hz=1e9, temperature_c=25.0)
        mc = MonteCarloConfig(
            mc_samples=30,
            seed=7,
            sigma_diameter_um=0.1,
            sigma_oxide_thickness_nm=2.0,
            sigma_metal_resistivity_ohm_m=1e-10,
            sigma_substrate_resistivity_ohm_cm=0.3,
            sigma_temperature_c=2.0,
        )

        out = run_monte_carlo_tsv(geometry, process, op, mc)
        self.assertEqual(out["samples"], 30)
        stats = out["statistics"]
        for metric in ("r_tsv_ohm", "l_tsv_h", "c_ox_f", "c_dep_f"):
            metric_stats = stats[metric]
            for key in ("mean", "std", "p5", "p50", "p95"):
                self.assertIn(key, metric_stats)
                self.assertTrue(math.isfinite(metric_stats[key]))


if __name__ == "__main__":
    unittest.main()
