# Phase 3 Migration Notes

Phase 3 files have been moved from the `phase2/` directory to the `phase3/` directory.

## File Structure

Phase 3 files are now located in:
```
phase3/
├── phase3_demo.py          # Main demo program
├── obstacle_detector.py    # Obstacle detection module
├── obstacle_avoider.py     # Obstacle avoidance control module
├── README.md               # Phase 3 overview
├── README_PHASE3.md        # Detailed documentation
├── QUICK_FIX.md            # Quick fix guide
├── RUN_WITHOUT_CRASHING.md # Crash prevention guide
├── INSTALL_BLOBCONVERTER.md # Installation guide
├── FIX_DISPLAY_ISSUE.md    # Display issue fixes
├── requirements.txt        # Dependencies list
├── start_phase3.sh         # Startup script
├── run_phase3_no_gui.sh    # No-GUI startup script
└── fix_opencv_display.sh   # Display fix script
```

## Dependencies

Phase 3 depends on shared modules from Phase 2:
- `oakd_camera.py` - OAKD camera interface
- `car_controller.py` - Vehicle control interface
- `person_follower.py` - Person tracking control logic

These modules remain in the `phase2/` directory, and Phase 3 will automatically import from there.

## Usage

Run Phase 3:

```bash
cd phase3
python phase3_demo.py --simulation --no-gui
```

The program will automatically import shared modules from `../phase2/`.

## Import Paths

Import paths in `phase3_demo.py` have been updated to:
1. First add the parent directory (project root) to the path (for `utils.py`)
2. Then add the `phase2/` directory to the path (for shared modules)

This allows Phase 3 to:
- Import `utils` from the project root directory
- Import shared modules (`oakd_camera`, `car_controller`, `person_follower`) from `phase2/`
- Import its own modules (`obstacle_detector`, `obstacle_avoider`) from `phase3/`

## Notes

- Phase 2 files remain unchanged, still in the `phase2/` directory
- Phase 3 depends on Phase 2's shared modules, so both directories need to exist
- If you modify Phase 2's shared modules, Phase 3 will automatically use the updated version
