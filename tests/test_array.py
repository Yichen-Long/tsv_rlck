import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tsv_rlck.extractor import extract_tsv_array
from tsv_rlck.models import OperatingPoint, TSVGeometry, TSVProcess


class ArrayTests(unittest.TestCase):
    def test_array_matrix_symmetry(self) -> None:
        g = TSVGeometry(diameter_um=10.0, height_um=60.0, oxide_thickness_nm=200.0, pitch_um=40.0)
        p = TSVProcess()
        op = OperatingPoint(frequency_hz=1e9)

        out = extract_tsv_array(g, p, op, rows=2, cols=2)
        m = out.mutual_l_h
        c = out.coupling_c_f

        self.assertEqual(len(out.node_order), 4)
        self.assertEqual(len(out.node_roles), 4)

        self.assertEqual(len(m), 4)
        self.assertEqual(len(c), 4)

        for i in range(4):
            self.assertEqual(m[i][i], 0.0)
            self.assertEqual(c[i][i], 0.0)
            for j in range(4):
                self.assertAlmostEqual(m[i][j], m[j][i], places=16)
                self.assertAlmostEqual(c[i][j], c[j][i], places=16)
    def test_gsg_topology_roles(self) -> None:
        g = TSVGeometry(diameter_um=10.0, height_um=60.0, oxide_thickness_nm=200.0, pitch_um=40.0)
        p = TSVProcess()
        op = OperatingPoint(frequency_hz=1e9)

        out = extract_tsv_array(g, p, op, rows=1, cols=3, topology="gsg")
        self.assertEqual(out.node_roles, ["G", "S", "G"])
        self.assertEqual(len(out.mutual_l_h), 3)
        self.assertEqual(len(out.coupling_c_f), 3)

    def test_diff_pair_topology_roles(self) -> None:
        g = TSVGeometry(diameter_um=10.0, height_um=60.0, oxide_thickness_nm=200.0, pitch_um=40.0)
        p = TSVProcess()
        op = OperatingPoint(frequency_hz=1e9)

        out = extract_tsv_array(g, p, op, rows=1, cols=2, topology="diff_pair")
        self.assertEqual(out.node_roles, ["P", "N"])
        self.assertEqual(len(out.mutual_l_h), 2)
        self.assertEqual(len(out.coupling_c_f), 2)

    def test_topology_shape_validation(self) -> None:
        g = TSVGeometry(diameter_um=10.0, height_um=60.0, oxide_thickness_nm=200.0, pitch_um=40.0)
        p = TSVProcess()
        op = OperatingPoint(frequency_hz=1e9)

        with self.assertRaises(ValueError):
            extract_tsv_array(g, p, op, rows=1, cols=2, topology="gsg")
        with self.assertRaises(ValueError):
            extract_tsv_array(g, p, op, rows=2, cols=2, topology="diff_pair")

