import json
import math
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tsv_rlck.sparams import extract_sparams, to_touchstone_s2p
from tsv_rlck.models import OperatingPoint, SweepConfig, TSVGeometry, TSVProcess


class SParamTests(unittest.TestCase):
    def test_touchstone_format_and_point_count(self) -> None:
        g = TSVGeometry(diameter_um=10.0, height_um=60.0, oxide_thickness_nm=200.0)
        p = TSVProcess()
        op = OperatingPoint(frequency_hz=1e9)
        sweep = SweepConfig(f_start_hz=1e6, f_stop_hz=1e9, points=5, spacing="lin")

        data = extract_sparams(g, p, op, sweep=sweep, z0=50.0)
        self.assertEqual(len(data["points"]), 5)

        txt = to_touchstone_s2p(data)
        lines = [ln for ln in txt.strip().splitlines() if ln.strip()]
        self.assertTrue(lines[0].startswith("# Hz S RI R"))
        self.assertEqual(len(lines), 6)
        for ln in lines[1:]:
            cols = ln.split()
            self.assertEqual(len(cols), 9)

    def test_sparams_are_bounded(self) -> None:
        g = TSVGeometry(diameter_um=10.0, height_um=60.0, oxide_thickness_nm=200.0)
        p = TSVProcess()
        op = OperatingPoint(frequency_hz=1e9, model_level="advanced")
        sweep = SweepConfig(f_start_hz=1e6, f_stop_hz=1e10, points=8, spacing="log")

        data = extract_sparams(g, p, op, sweep=sweep, z0=50.0)
        for pt in data["points"]:
            s11 = complex(pt["s11_re"], pt["s11_im"])
            s21 = complex(pt["s21_re"], pt["s21_im"])
            s12 = complex(pt["s12_re"], pt["s12_im"])
            s22 = complex(pt["s22_re"], pt["s22_im"])
            self.assertTrue(math.isfinite(abs(s11)))
            self.assertTrue(math.isfinite(abs(s21)))
            self.assertTrue(math.isfinite(abs(s12)))
            self.assertTrue(math.isfinite(abs(s22)))
            self.assertLess(abs(s11), 2.0)
            self.assertLess(abs(s21), 2.0)
    def test_sparams_include_topology_metadata(self) -> None:
        g = TSVGeometry(diameter_um=10.0, height_um=60.0, oxide_thickness_nm=200.0, pitch_um=40.0)
        p = TSVProcess()
        op = OperatingPoint(frequency_hz=1e9)

        data = extract_sparams(g, p, op, rows=1, cols=3, pitch_um=40.0, topology="gsg")
        self.assertEqual(data["topology"], "gsg")
        self.assertEqual(data["node_roles"], ["G", "S", "G"])
        self.assertEqual(data["node_order"], ["N0", "N1", "N2"])

