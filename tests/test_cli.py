import json
import math
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tsv_rlck.cli import main


class CliTests(unittest.TestCase):
    def test_cli_generates_json_and_spice(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out_json = Path(td) / "out.json"
            out_sp = Path(td) / "out.sp"
            rc = main(
                [
                    "--diameter-um", "10",
                    "--height-um", "60",
                    "--oxide-thickness-nm", "200",
                    "--frequency-hz", "1e9",
                    "--pitch-um", "40",
                    "--rows", "2",
                    "--cols", "2",
                    "--json-out", str(out_json),
                    "--spice-out", str(out_sp),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(out_json.exists())
            self.assertTrue(out_sp.exists())
            txt = out_sp.read_text(encoding="utf-8")
            self.assertIn(".subckt TSV_RLCK", txt)
            self.assertIn("RTSV", txt)
            self.assertIn("LTSV", txt)

    def test_cli_sweep_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out_json = Path(td) / "sweep.json"
            rc = main(
                [
                    "--diameter-um", "10",
                    "--height-um", "60",
                    "--oxide-thickness-nm", "200",
                    "--frequency-hz", "1e9",
                    "--json-out", str(out_json),
                    "--sweep-start-hz", "1e6",
                    "--sweep-stop-hz", "1e9",
                    "--sweep-points", "5",
                    "--sweep-spacing", "lin",
                ]
            )
            self.assertEqual(rc, 0)
            data = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertIn("sweep", data)
            self.assertEqual(len(data["sweep"]["frequency_hz"]), 5)
            self.assertEqual(len(data["sweep"]["r_tsv_ohm"]), 5)
            self.assertAlmostEqual(data["sweep"]["frequency_hz"][0], 1e6)
            self.assertAlmostEqual(data["sweep"]["frequency_hz"][-1], 1e9)

    def test_cli_monte_carlo_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out_json = Path(td) / "mc.json"
            rc = main(
                [
                    "--diameter-um", "10",
                    "--height-um", "60",
                    "--oxide-thickness-nm", "200",
                    "--frequency-hz", "1e9",
                    "--json-out", str(out_json),
                    "--mc-samples", "20",
                    "--seed", "42",
                    "--sigma-diameter-um", "0.1",
                    "--sigma-oxide-thickness-nm", "2.0",
                    "--sigma-metal-resistivity-ohm-m", "1e-10",
                    "--sigma-substrate-resistivity-ohm-cm", "0.2",
                    "--sigma-temperature-c", "2.0",
                ]
            )
            self.assertEqual(rc, 0)
            data = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertIn("monte_carlo", data)
            self.assertEqual(data["monte_carlo"]["samples"], 20)
            for metric in ("r_tsv_ohm", "l_tsv_h", "c_ox_f", "c_dep_f"):
                stats = data["monte_carlo"]["statistics"][metric]
                for k in ("mean", "std", "p5", "p50", "p95"):
                    self.assertIn(k, stats)
                    self.assertTrue(math.isfinite(stats[k]))

    def test_cli_benchmark_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out_json = Path(td) / "bm.json"
            benchmark_file = Path(td) / "reference.json"
            benchmark_file.write_text(
                json.dumps(
                    {
                        "input": {
                            "geometry": {"diameter_um": 10.0, "height_um": 60.0, "oxide_thickness_nm": 200.0},
                            "process": {
                                "metal_resistivity_ohm_m": 1.68e-8,
                                "substrate_resistivity_ohm_cm": 10.0,
                                "substrate_doping_cm3": 1.0e15,
                                "eps_ox_rel": 3.9,
                                "eps_si_rel": 11.7,
                            },
                            "operating_point": {"frequency_hz": 1e9, "temperature_c": 25.0, "bias_v": 0.0},
                        },
                        "reference": {
                            "r_tsv_ohm": 0.1,
                            "l_tsv_h": 1e-11,
                            "c_ox_f": 1e-14,
                            "c_dep_f": 1e-14,
                        },
                    }
                ),
                encoding="utf-8",
            )
            rc = main(
                [
                    "--diameter-um", "10",
                    "--height-um", "60",
                    "--oxide-thickness-nm", "200",
                    "--frequency-hz", "1e9",
                    "--json-out", str(out_json),
                    "--benchmark-file", str(benchmark_file),
                ]
            )
            self.assertEqual(rc, 0)
            data = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertIn("benchmark_report", data)
            self.assertIn("summary", data["benchmark_report"])


if __name__ == "__main__":
    unittest.main()
