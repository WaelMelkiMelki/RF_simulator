# Runtime repair validation

## Earlier execution in the prepared Python 3.12 environment

- The original requirements installation failed on an absolute Windows editable-install path.
- The replacement requirements installed successfully and `pip check` reported no broken requirements.
- The then-current existing suite produced 95 passed and 1 skipped. This is a historical result, not a result for the final patch.
- The repaired CLI produced 300 finite coverage values and CSV/JSON exports from the synthetic scene. Loading the bundled OBJ also produced an export.
- An offscreen desktop launch reached application startup, but VTK reported OpenGL shader errors. Interactive 3D rendering is not verified.

## Current verification limit

The temporary environment did not persist into the resumed session. The current interpreter lacks pytest, PyVista, PyQt6 and other required packages. No packages or virtual environments were installed after the user's request to avoid downloads. Syntax, CLI argument validation and missing-dependency diagnostics can be checked without them.

Five regression tests were added for CLI exports and input validation, selected-model preservation above 1,000 points, analytical free-space loss, repeated properties-panel configuration and actual material propagation. The latest fixes to the regression tests and merged Scene3D class still require a complete rerun. Do not interpret the earlier 95-pass result as verification of this final state.

## Behavior changes and remaining limits

- Large-grid calculations now use the selected model consistently, with reduced throughput versus the old unconditional free-space vectorization.
- Free-space calculations no longer receive an extra obstacle penalty; material-aware models own their attenuation calculation.
- The shadowed Scene3D material propagation implementation is restored.
- CLI creates a transmitter, validates numeric arguments and exports structured results; failures return a nonzero exit code.
- GUI diagnostics do not install packages or change the user's Python environment.
- Physical model accuracy and desktop OpenGL rendering require separate validation. The project remains an approximate simulator.

Before marking the repair ready, rerun `python -m pytest tests -q` in a compatible existing environment, run the synthetic CLI demo and inspect the GUI on a desktop with working OpenGL.
