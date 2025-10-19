# DNA Editor - Developer Quickstart

A standalone 3D interactive tool for designing procedural tentacle creatures using mathematical curve algorithms.

## Quick Start

```bash
# From project root
python3 dna_editor/main_qt.py

# Or directly from the folder
cd dna_editor
python3 main_qt.py
```

## What It Does

Creates animated 3D tentacle creatures using two mathematical algorithms:
- **Bezier Curves** - Smooth cubic polynomial curves
- **Fourier Series** - Organic wave-based shapes

Real-time parameter adjustment with PyQt6 sliders/controls, presets, and undo/redo system. 3D preview in separate Ursina window.

## Architecture

**Clean modular design** - PyQt6 UI with shared core logic

```
dna_editor/
├── main_qt.py                   # Entry point (~70 lines)
│
├── core/                        # Math & Config (no dependencies)
│   ├── curves.py               # Bezier & Fourier generators
│   └── constants.py            # All configuration values
│
├── models/                      # 3D Entities (Ursina)
│   ├── tentacle.py             # Single animated tentacle
│   └── creature.py             # Body + tentacles
│
├── qt_ui/                       # PyQt6 UI Components
│   ├── editor_window.py        # Main window with menu bar
│   ├── control_panel.py        # Left panel with all controls
│   ├── viewport_widget.py      # 3D viewport wrapper
│   └── ursina_renderer.py      # Alternative renderer (experimental)
│
└── controllers/                 # Application Logic
    └── state_manager.py        # Undo/redo history (50 steps)
```

## Key Files

- **`qt_ui/editor_window.py`** - Main window orchestration, menu bar, keyboard shortcuts
- **`qt_ui/control_panel.py`** - All UI controls (sliders, spinboxes, buttons)
- **`qt_ui/viewport_widget.py`** - Ursina 3D rendering in separate window
- **`core/curves.py`** - Pure mathematical curve generators (testable)
- **`models/creature.py`** - Creature entity with tentacles
- **`controllers/state_manager.py`** - Undo/redo state management

## Development Notes

- **Pure math in `core/`** - No Ursina dependencies, easily testable
- **PyQt6 UI** - Native OS widgets, standard layouts
- **Separate 3D window** - Ursina renders in its own window (not embedded)
- **State management** - Centralized history for undo/redo
- **No external assets** - All graphics procedurally generated

## UI Features

- **Control Panel** (left side):
  - Tentacle count spinbox
  - Segment count spinbox
  - Algorithm dropdown (Bezier/Fourier)
  - Algorithm-specific parameter sliders
  - Thickness and taper sliders
  - Preset buttons
  - Undo/Redo buttons
  - Export JSON button

- **3D Viewport** (separate window):
  - Real-time creature preview
  - Mouse drag to rotate camera
  - Scroll to zoom
  - Press R to reset camera

- **Menu Bar**:
  - File → Export JSON (Ctrl+E)
  - Edit → Undo (Ctrl+Z), Redo (Ctrl+Y)
  - Help → About

## Keyboard Shortcuts

```
Ctrl+Z      - Undo
Ctrl+Y      - Redo
Ctrl+E      - Export JSON
Ctrl+Q      - Quit
R           - Reset camera (in 3D window)
```

## Making Changes

1. **Add a new algorithm?** → Add generator to `core/curves.py`, update `core/constants.py`, add UI controls to `qt_ui/control_panel.py`
2. **Change UI layout?** → Modify `qt_ui/control_panel.py` or `qt_ui/editor_window.py`
3. **Add new controls?** → Update `qt_ui/control_panel.py` and emit signals to `editor_window.py`
4. **Adjust animation?** → Edit `models/tentacle.py` update logic
5. **Change 3D rendering?** → Modify `qt_ui/viewport_widget.py`

## Dependencies

- **PyQt6** - UI framework
- **Ursina Engine** - 3D rendering (built on Panda3D)
- **Python 3.8+**
- **Math** (standard library)

## Integration with Roguelike

This tool is designed to generate tentacle DNA for creatures in the main roguelike game. Use the "Export JSON" feature to save configurations for import into `entities.py`.

---

**For user documentation:** See `README.md`
**For PyQt6 technical details:** See `PYQT6_VERSION.md`
