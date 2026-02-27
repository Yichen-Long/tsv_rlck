from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .benchmark import compare_batch_against_reference, compare_single_against_reference, summarize_error
from .extractor import extract_single_tsv, extract_sweep_tsv, extract_tsv_array, run_monte_carlo_tsv
from .models import MonteCarloConfig, OperatingPoint, SweepConfig, TSVGeometry, TSVProcess
from .spice import to_spice_subckt
from .sparams import extract_sparams, to_touchstone_s2p


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="TSV RLCK analytical extractor")
    p.add_argument("--diameter-um", type=float, required=True)
    p.add_argument("--height-um", type=float, required=True)
    p.add_argument("--oxide-thickness-nm", type=float, required=True)
    p.add_argument("--pitch-um", type=float, default=None)
    p.add_argument("--frequency-hz", type=float, required=True)
    p.add_argument("--temperature-c", type=float, default=25.0)
    p.add_argument("--bias-v", type=float, default=0.0)
    p.add_argument("--model-level", choices=("simple", "advanced"), default="simple")
    p.add_argument("--substrate-resistivity-ohm-cm", type=float, default=10.0)
    p.add_argument("--substrate-doping-cm3", type=float, default=1.0e15)
    p.add_argument("--metal-resistivity-ohm-m", type=float, default=1.68e-8)
    p.add_argument("--eps-ox-rel", type=float, default=3.9)
    p.add_argument("--eps-si-rel", type=float, default=11.7)
    p.add_argument("--rows", type=int, default=1)
    p.add_argument("--cols", type=int, default=1)
    p.add_argument("--topology", choices=("grid", "gsg", "diff_pair"), default="grid")

    p.add_argument("--sweep-start-hz", type=float, default=None)
    p.add_argument("--sweep-stop-hz", type=float, default=None)
    p.add_argument("--sweep-points", type=int, default=None)
    p.add_argument("--sweep-spacing", choices=("lin", "log"), default="lin")

    p.add_argument("--mc-samples", type=int, default=0)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--sigma-diameter-um", type=float, default=0.0)
    p.add_argument("--sigma-oxide-thickness-nm", type=float, default=0.0)
    p.add_argument("--sigma-metal-resistivity-ohm-m", type=float, default=0.0)
    p.add_argument("--sigma-substrate-resistivity-ohm-cm", type=float, default=0.0)
    p.add_argument("--sigma-temperature-c", type=float, default=0.0)

    p.add_argument("--benchmark-file", type=Path, default=None)
    p.add_argument("--benchmark-batch-file", type=Path, default=None)
    p.add_argument("--benchmark-report-out", type=Path, default=None)

    p.add_argument("--sparams-out", type=Path, default=None)
    p.add_argument("--z0", type=float, default=50.0)

    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--spice-out", type=Path, default=None)
    p.add_argument("--subckt-name", type=str, default="TSV_RLCK")
    return p


def _from_input_override(
    geometry: TSVGeometry,
    process: TSVProcess,
    op: OperatingPoint,
    benchmark_data: dict[str, object],
) -> tuple[TSVGeometry, TSVProcess, OperatingPoint]:
    input_data = benchmark_data.get("input")
    if not isinstance(input_data, dict):
        return geometry, process, op

    g = input_data.get("geometry") if isinstance(input_data.get("geometry"), dict) else {}
    p = input_data.get("process") if isinstance(input_data.get("process"), dict) else {}
    o = input_data.get("operating_point") if isinstance(input_data.get("operating_point"), dict) else {}

    geometry = TSVGeometry(
        diameter_um=float(g.get("diameter_um", geometry.diameter_um)),
        height_um=float(g.get("height_um", geometry.height_um)),
        oxide_thickness_nm=float(g.get("oxide_thickness_nm", geometry.oxide_thickness_nm)),
        pitch_um=g.get("pitch_um", geometry.pitch_um),
    )
    process = TSVProcess(
        metal_resistivity_ohm_m=float(p.get("metal_resistivity_ohm_m", process.metal_resistivity_ohm_m)),
        substrate_resistivity_ohm_cm=float(p.get("substrate_resistivity_ohm_cm", process.substrate_resistivity_ohm_cm)),
        substrate_doping_cm3=float(p.get("substrate_doping_cm3", process.substrate_doping_cm3)),
        eps_ox_rel=float(p.get("eps_ox_rel", process.eps_ox_rel)),
        eps_si_rel=float(p.get("eps_si_rel", process.eps_si_rel)),
    )
    op = OperatingPoint(
        frequency_hz=float(o.get("frequency_hz", op.frequency_hz)),
        temperature_c=float(o.get("temperature_c", op.temperature_c)),
        bias_v=float(o.get("bias_v", op.bias_v)),
        model_level=str(o.get("model_level", op.model_level)),
    )
    return geometry, process, op


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    geometry = TSVGeometry(
        diameter_um=args.diameter_um,
        height_um=args.height_um,
        oxide_thickness_nm=args.oxide_thickness_nm,
        pitch_um=args.pitch_um,
    )
    process = TSVProcess(
        metal_resistivity_ohm_m=args.metal_resistivity_ohm_m,
        substrate_resistivity_ohm_cm=args.substrate_resistivity_ohm_cm,
        substrate_doping_cm3=args.substrate_doping_cm3,
        eps_ox_rel=args.eps_ox_rel,
        eps_si_rel=args.eps_si_rel,
    )
    op = OperatingPoint(
        frequency_hz=args.frequency_hz,
        temperature_c=args.temperature_c,
        bias_v=args.bias_v,
        model_level=args.model_level,
    )

    if args.rows == 1 and args.cols == 1:
        single = extract_single_tsv(geometry, process, op)
        payload = {
            "single": asdict(single),
            "array": None,
            "model_level": op.model_level,
        }
    else:
        arr = extract_tsv_array(
            geometry,
            process,
            op,
            rows=args.rows,
            cols=args.cols,
            pitch_um=args.pitch_um,
            topology=args.topology,
        )
        payload = {
            "single": asdict(arr.single),
            "array": {
                "topology": args.topology,
                "node_order": arr.node_order,
                "node_roles": arr.node_roles,
                "mutual_l_h": arr.mutual_l_h,
                "coupling_c_f": arr.coupling_c_f,
            },
            "model_level": op.model_level,
        }

    if args.sweep_start_hz is not None or args.sweep_stop_hz is not None or args.sweep_points is not None:
        if args.sweep_start_hz is None or args.sweep_stop_hz is None or args.sweep_points is None:
            raise ValueError("sweep requires --sweep-start-hz, --sweep-stop-hz and --sweep-points")
        sweep = SweepConfig(
            f_start_hz=args.sweep_start_hz,
            f_stop_hz=args.sweep_stop_hz,
            points=args.sweep_points,
            spacing=args.sweep_spacing,
        )
        payload["sweep"] = extract_sweep_tsv(geometry, process, op, sweep)

    if args.mc_samples > 0:
        mc = MonteCarloConfig(
            mc_samples=args.mc_samples,
            seed=args.seed,
            sigma_diameter_um=args.sigma_diameter_um,
            sigma_oxide_thickness_nm=args.sigma_oxide_thickness_nm,
            sigma_metal_resistivity_ohm_m=args.sigma_metal_resistivity_ohm_m,
            sigma_substrate_resistivity_ohm_cm=args.sigma_substrate_resistivity_ohm_cm,
            sigma_temperature_c=args.sigma_temperature_c,
        )
        payload["monte_carlo"] = run_monte_carlo_tsv(geometry, process, op, mc)

    if args.benchmark_file is not None:
        benchmark_data = json.loads(args.benchmark_file.read_text(encoding="utf-8"))
        geometry_eval, process_eval, op_eval = _from_input_override(geometry, process, op, benchmark_data)
        reference = benchmark_data.get("reference")
        if not isinstance(reference, dict):
            raise ValueError("benchmark reference must be a JSON object")
        report = compare_single_against_reference(geometry_eval, process_eval, op_eval, reference)
        payload["benchmark_report"] = {
            "details": report,
            "summary": summarize_error(report),
        }

    if args.benchmark_batch_file is not None:
        benchmark_batch = json.loads(args.benchmark_batch_file.read_text(encoding="utf-8"))
        cases = benchmark_batch.get("cases")
        if not isinstance(cases, list):
            raise ValueError("benchmark batch file must contain a cases array")
        payload["benchmark_batch_report"] = compare_batch_against_reference(cases, default_model_level=op.model_level)

    print(json.dumps(payload, indent=2))

    if args.json_out is not None:
        args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.benchmark_report_out is not None:
        report_payload = {
            "benchmark_report": payload.get("benchmark_report"),
            "benchmark_batch_report": payload.get("benchmark_batch_report"),
        }
        args.benchmark_report_out.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")

    if args.spice_out is not None:
        spice_text = to_spice_subckt(
            extract_single_tsv(geometry, process, op),
            op=op,
            name=args.subckt_name,
        )
        args.spice_out.write_text(spice_text, encoding="utf-8")

    if args.sparams_out is not None:
        sweep_cfg = None
        if args.sweep_start_hz is not None and args.sweep_stop_hz is not None and args.sweep_points is not None:
            sweep_cfg = SweepConfig(
                f_start_hz=args.sweep_start_hz,
                f_stop_hz=args.sweep_stop_hz,
                points=args.sweep_points,
                spacing=args.sweep_spacing,
            )
        sparams = extract_sparams(geometry, process, op, sweep=sweep_cfg, z0=args.z0)
        payload["sparams"] = sparams
        args.sparams_out.write_text(to_touchstone_s2p(sparams), encoding="utf-8")

    return 0
