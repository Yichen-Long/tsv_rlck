import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tsv_rlck.benchmark import (
    compare_batch_against_reference,
    compare_single_against_reference,
    summarize_error,
)
from tsv_rlck.models import OperatingPoint, TSVGeometry, TSVProcess


class BenchmarkTests(unittest.TestCase):
    def test_error_report_contains_metrics(self) -> None:
        geometry = TSVGeometry(diameter_um=10.0, height_um=60.0, oxide_thickness_nm=200.0)
        process = TSVProcess()
        op = OperatingPoint(frequency_hz=1e9)
        reference = {
            "r_tsv_ohm": 0.1,
            "l_tsv_h": 1e-11,
            "c_ox_f": 1e-14,
            "c_dep_f": 1e-14,
        }

        report = compare_single_against_reference(geometry, process, op, reference)
        self.assertIn("r_tsv_ohm", report)
        self.assertIn("abs_error", report["r_tsv_ohm"])
        self.assertIn("rel_error_pct", report["r_tsv_ohm"])

        summary = summarize_error(report)
        self.assertIn("mae", summary)
        self.assertIn("mape_pct", summary)
        self.assertIn("rmse", summary)
        self.assertGreaterEqual(summary["max_abs_error"], 0.0)
        self.assertGreaterEqual(summary["max_rel_error_pct"], 0.0)

    def test_batch_benchmark_report(self) -> None:
        cases = [
            {
                "name": "c1",
                "input": {
                    "geometry": {"diameter_um": 10.0, "height_um": 60.0, "oxide_thickness_nm": 200.0},
                    "process": {"metal_resistivity_ohm_m": 1.68e-8, "substrate_resistivity_ohm_cm": 10.0},
                    "operating_point": {"frequency_hz": 1e9},
                },
                "reference": {
                    "r_tsv_ohm": 0.1,
                    "l_tsv_h": 1e-11,
                    "c_ox_f": 1e-14,
                    "c_dep_f": 1e-14,
                },
            },
            {
                "name": "c2",
                "input": {
                    "geometry": {"diameter_um": 8.0, "height_um": 50.0, "oxide_thickness_nm": 150.0},
                    "process": {"metal_resistivity_ohm_m": 1.8e-8, "substrate_resistivity_ohm_cm": 8.0},
                    "operating_point": {"frequency_hz": 5e9, "model_level": "advanced"},
                },
                "reference": {
                    "r_tsv_ohm": 0.12,
                    "l_tsv_h": 8e-12,
                    "c_ox_f": 8e-15,
                    "c_dep_f": 8e-15,
                },
            },
        ]

        report = compare_batch_against_reference(cases)
        self.assertIn("cases", report)
        self.assertIn("overall", report)
        self.assertEqual(report["overall"]["cases"], 2)
        self.assertIn("mean_rmse", report["overall"])


if __name__ == "__main__":
    unittest.main()
