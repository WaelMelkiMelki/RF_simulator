#!/usr/bin/env python3
"""Run a reproducible CPU coverage simulation without opening a GUI."""
import argparse
import json
import logging
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))


def positive(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError('must be finite and greater than zero')
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', '-s', help='OBJ/GLB/GLTF scene; defaults to a synthetic 10 m box')
    parser.add_argument('--output', '-o', default='simulation_results', help='Output directory')
    parser.add_argument('--frequency', '-f', type=positive, default=2400., help='Frequency in MHz')
    parser.add_argument('--power', '-p', type=float, default=20., help='Transmit power in dBm')
    parser.add_argument('--resolution', '-r', type=positive, default=1., help='Grid spacing in metres')
    parser.add_argument('--model', choices=['free_space', 'ray_tracing', 'material_aware'], default='free_space')
    parser.add_argument('--position', nargs=3, type=float, default=[0., 0., 1.5], metavar=('X', 'Y', 'Z'))
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args(argv)
    if not all(math.isfinite(x) for x in [args.power, *args.position]):
        parser.error('power and position must be finite')
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    try:
        import numpy as np
        import pyvista as pv
        from core.application.simulation_orchestrator import SimulationOrchestrator
        from core.application.exporter import ExportManager
        from core.domain.antenna_factory import AntennaFactory
        from core.domain.scene import Scene3D

        orchestrator = SimulationOrchestrator()
        if args.scene:
            orchestrator.load_scene(args.scene)
        else:
            scene = Scene3D()
            scene.load_from_data(pv.Box(bounds=(-5., 5., -5., 5., 0., 3.)))
            orchestrator.set_scene(scene)
        orchestrator.add_antenna(AntennaFactory().create_antenna('wifi', {
            'name': 'CLI transmitter', 'position': args.position,
            'frequency': args.frequency * 1e6, 'power_dbm': args.power,
        }))
        config = {'resolution': args.resolution, 'propagation_model': args.model,
                  'rf_calculator_backend': 'optimized', 'visualization_mode': 'heatmap'}
        results = orchestrator.start_simulation(config)
        points, values = np.asarray(results['points']), np.asarray(results['values'])
        if not len(points) or len(points) != len(values) or not np.isfinite(values).all():
            raise ValueError('Simulation returned empty, mismatched or non-finite coverage')
        output = Path(args.output)
        output.mkdir(parents=True, exist_ok=True)
        coverage = {'coverage': [{'position': p.tolist(), 'signal_strength': float(v)}
                                  for p, v in zip(points, values)]}
        ExportManager().export(coverage, 'csv', str(output / 'coverage.csv'), config)
        (output / 'coverage.json').write_text(json.dumps({
            'points': points.tolist(), 'values': values.tolist(), 'config': config,
            'frequency_hz': args.frequency * 1e6, 'power_dbm': args.power,
        }, indent=2), encoding='utf-8')
        print(f'Simulated {len(points)} points. Results: {output.resolve()}')
        return 0
    except Exception:
        logging.exception('Simulation failed')
        return 1


if __name__ == '__main__':
    sys.exit(main())
