# RF Simulator 3D

Desktop and command-line RF coverage simulation using Python, PyQt6 and PyVista/VTK. Supports free-space and material-aware propagation, 3D scenes and CSV/JSON exports. These are approximate simulation models, not calibrated engineering predictions.

## Run with your existing Python installation

Python 3.11+ is declared; the previous runtime checks used Python 3.12. From this repository folder, use the Python interpreter where your project dependencies are already installed. No virtual environment is required, and these commands do not download or install anything:

```sh
python src/main.py --check
python cli.py --output simulation_results
python src/main.py
```

The first command checks dependencies and GUI imports without opening a window. It reports missing dependencies and exits; it never installs them automatically. The second runs a CPU simulation in a synthetic 10 m × 10 m × 3 m box and writes `coverage.csv` and `coverage.json`. The third opens the desktop UI and requires a working graphical display and OpenGL driver.

For an existing scene:

```sh
python cli.py --scene data/test_scene.obj --resolution 0.25 --output simulation_results/obj
```

Frequency is in MHz, power in dBm, positions and grid spacing in metres. See `python cli.py --help`. A default transmitter is created automatically. The CLI does not open a GUI, but currently still depends on the project's PyVista/VTK application stack.

## Missing dependencies / limited internet

If the checks report missing packages, the application cannot run until those dependencies are supplied. Do not run an online installation on a limited connection. Reuse your existing interpreter first. Alternatively, a compatible offline wheel folder can be prepared on another machine with good internet (matching your operating system, CPU and Python version) and transferred by USB. This project does not include that folder.

For a machine where installing dependencies is acceptable, `requirements.txt` records the repaired environment. The following is optional and downloads packages:

```sh
git clone https://github.com/WaelMelkiMelki/RF_simulator.git
cd RF_simulator
python -m pip install -r requirements.txt
```

The old requirements contained a developer-specific Windows path and conflicting Qt/PDF packages. The replacement uses PyQt6 and fpdf2. No PyTorch download is required. Do not mix this dependency set into another project's environment without reviewing potential version conflicts.

## Validation

With dependencies already present, run:

```sh
python -m pytest tests -q
```

For a headless Linux test runner set `QT_QPA_PLATFORM=offscreen`, `MPLBACKEND=Agg` and `PYTHONUTF8=1`. This permits widget checks but does not prove that the interactive 3D viewport renders correctly.

See [runtime validation](docs/RUNTIME_VALIDATION.md) for the tested scope and outstanding checks. Large grids now preserve the selected propagation model; the former fast vectorized path ignored that selection. This correctness fix sacrifices its advertised speedup.

## Source layout

- `src/gui`: desktop presentation and widgets
- `src/core/application`: simulation orchestration, calculation and exports
- `src/core/domain`: scenes, antennas and propagation models
- `src/core/infrastructure`: loaders and supporting services
- `cli.py`: CPU simulation entry point
- `tests`: domain, integration and runtime regression tests

Architecture references: [Mermaid source](docs/architecture.mmd), [PlantUML source](docs/architecture.puml).
