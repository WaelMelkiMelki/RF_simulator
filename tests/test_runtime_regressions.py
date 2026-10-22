"""End-to-end and numerical regressions for the repaired launch paths."""
import json
import os
from pathlib import Path
import subprocess
import sys
import numpy as np
import pytest
from core.application.optimized_rf_calculator import OptimizedRFCalculator
from core.domain.rf_models import FreeSpaceModel

ROOT = Path(__file__).resolve().parents[1]


def test_cli_exports_and_rejects_invalid_resolution(tmp_path):
    output = tmp_path / 'results'
    run = subprocess.run([sys.executable, str(ROOT / 'cli.py'), '--output', str(output)],
                         cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", timeout=45)
    assert run.returncode == 0, run.stderr
    data = json.loads((output / 'coverage.json').read_text())
    assert len(data['points']) == len(data['values']) == 300
    assert np.isfinite(data['values']).all()
    assert len((output / 'coverage.csv').read_text().splitlines()) == 301
    bad = subprocess.run([sys.executable, str(ROOT / 'cli.py'), '-r', '0'],
                         capture_output=True, text=True, encoding="utf-8", timeout=10)
    assert bad.returncode == 2


def test_large_grid_preserves_selected_model(test_scene, wifi_antenna):
    class ConstantLoss:
        def calculate_path_loss(self, *args):
            return 60.
    calculator = OptimizedRFCalculator(test_scene, [wifi_antenna], ConstantLoss(),
                                       use_parallel=True, use_spatial_cache=False)
    result = calculator.calculate_coverage_grid_detailed(resolution=.09)
    assert len(result['points']) > 1000
    assert result['values'] == pytest.approx([wifi_antenna.power_dbm - 60.] * len(result['points']))


def test_free_space_does_not_add_obstacle_penalties(test_scene, wifi_antenna):
    calculator = OptimizedRFCalculator(test_scene, [wifi_antenna], FreeSpaceModel())
    point = [10., 0., 1.]
    expected = wifi_antenna.power_dbm - 20 * np.log10(4 * np.pi * 10 * wifi_antenna.frequency / 3e8)
    assert calculator._calculate_total_signal_at_point_optimized(point) == pytest.approx(expected)


def test_properties_panel_without_torch():
    code = '''
from PyQt6.QtWidgets import QApplication
from gui.widgets.properties_panel import PropertiesPanel
app = QApplication([])
panel = PropertiesPanel()
for _ in range(3):
    panel.set_simulation_config({'resolution': 2., 'model': 'Free Space'})
    app.processEvents()
    assert panel.get_simulation_config()['resolution'] == 2.
panel.close()
'''
    env = {**os.environ, 'QT_QPA_PLATFORM': 'offscreen'}
    result = subprocess.run([sys.executable, '-c', code], env=env,
                            capture_output=True, text=True, encoding="utf-8", timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr


def test_material_propagation_is_not_replaced_with_noop(test_scene):
    mesh = test_scene.mesh
    mesh.field_data['mesh_origins'] = ['wall']
    mesh.cell_data['mesh_origin_id'] = np.zeros(mesh.n_cells, dtype=int)
    test_scene.mesh_material_mapping['wall'] = 'concrete'
    test_scene.propagate_materials_to_cells()
    assert list(mesh.cell_data['material_name']) == ['concrete'] * mesh.n_cells
