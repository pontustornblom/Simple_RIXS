# Simple RIXS

**Note:** If you are reading this file locally (in Notepad, for example), the formatting will not display correctly. The properly formatted version is at https://github.com/pontustornblom/Simple_RIXS

Simple RIXS is a PyQt5 desktop application for automated routine analysis of RIXS (Resonant Inelastic X-ray Scattering) data from synchrotron beamline experiments. It focuses on high throughput and an easy to use graphical user interface. It can also handle some XAS (X-ray Absorption Spectroscopy) but it has not been the primary purpose, unless you wish to extract TFY, PFY or iPFY XAS from RIXS data.

Developed by Pontus Törnblom, Uppsala University.

---

## Supported beamlines

| Facility | Country | Mode |
|---|---|---|
| MAX IV — Veritas | Sweden | RIXS, XAS, time-resolved RIXS |
| MAX IV — Species | Sweden | RIXS, XAS |
| SPring-8 — BL27SU | Japan | RIXS |
| SOLEIL — Galaxies | France | RIXS |
| ALS | USA | RIXS, XAS |
| Diamond | UK | RIXS, XAS |
| NanoTerasu — BL02U | Japan | RIXS (experimental) |
| And possibly more |

---

## Features

- Interactive GUI wizard. A series of dialogs guides you through every processing step, no command-line arguments needed
- Facility-specific and generic raw data importers for HDF5 (.h5) and text formats
- High throughput data treatment by automating repetitive tasks and shared parameters for each set of beamtime data
- Elastic peak alignment using a three-pass converging algorithm (weighted centroid + Gaussian fit)
- Waterfall plots comparing multiple RIXS or XAS spectra from different files
- Savitzky-Golay and Gaussian smoothing with eV-based window sizes
- Binning
- Energy axis switching between emission energy and energy loss views
- PFY (Partial Fluorescence Yield) extraction from RIXS maps
- XAS normalization and background subtraction
- Spectral subtraction for both line scans and full RIXS maps
- Time-resolved RIXS analysis for Veritas DLD detector data, dividing a measurement into time windows using actual timestamps
- All output saved as tab-separated `.txt` files compatible with other analysis tools

---

## Requirements

**Python 3.10 or newer.** If you don't already have it, download it
from [python.org](https://www.python.org/downloads/) and tick
"Add python.exe to PATH" during installation.

Then install the dependencies from a terminal:

```bash
pip install numpy scipy h5py pandas matplotlib PyQt5
```

**A text editor.** You will need to edit one line in `Simple_RIXS.py` to point at your data folder (see Quick start below). Notepad works, but [Visual Studio Code](https://code.visualstudio.com/) is recommended. It also lets you run the program by pressing F5, without using a terminal.

---

## Download and Installation

Either clone the repository:

```bash
git clone https://github.com/pontustornblom/Simple_RIXS.git
```

Or, if you don't have git: click the green **Code** button at the top
of this page, choose **Download ZIP**, and extract it anywhere.

No build or compile step is required. The application is pure Python and runs directly from the cloned folder.

---

## Quick start

**Note:** If you are reading this file locally (in Notepad, for example), the formatting will not display correctly. The properly formatted version is at https://github.com/pontustornblom/Simple_RIXS

**Step 1.** Copy `Simple_RIXS.py` and rename the copy for your beamtime session, for example `Simple_RIXS_2025_11_Veritas.py`. Keeping one copy per dataset means each session retains its own folder path and settings.

**Step 2.** Open the copy and set the project folder path near the top of the file to where your raw data is stored. Here is an example:

```python
input_file_project_folder = "C:\\Users\\Pontus\\Data\\2025_11_Veritas"
```
This will make the parameters you set during data treatment to apply to this specific dataset, reducing the amount of repetitive work you need to spend to treat all data.

**Step 3.** Run the script (press F5 in VS Code, or `python Simple_RIXS_2025_11_Veritas.py` in a terminal). A GUI window will open and guide you through the rest. Note that some of the options in the drop-down menu might not yet be available.


### Workflow
The general workflow has two stages.

First, convert the raw beamline data into a treated format using one of the `Make treated RIXS...` options in the drop-down menu.

Once you have treated data, you can perform more advanced operations. Select the operation you want from the drop-down menu and use the treated files as input.

Output is saved automatically to a `Simple_RIXS_figures/` subfolder inside your project folder. The current parameters controlling the program are stored in `parameters.txt` inside the `Simple_RIXS_parameters/` subfolder.

One particularly useful option is `Replot treated spectra`, which reads the parameters from a selected file so you can adjust an already-saved plot. Note that this may require the original beamline raw data to still be available, depending on how the plot was produced.

### Buttons

| Button | What it does |
|---|---|
| `Save and continue` | Saves the parameters from this window and moves to the next step. Eventually saving the data and figure. |
| `Save and close` | Saves the parameters and closes the program. |
| `Close` | Closes the window **without** saving the parameters you entered. |
| `Update the plot` | Applies your current inputs to the displayed plot. Press this before `Save and continue` if you changed anything, so the changes take effect. |

### Troubleshooting

**The program crashes when I press `Update the plot`.**
Bad input values cause a crash before the parameters are saved, so you have to enter them again on restart. If this happens often, press `Save and close` every so often and restart. This checkpoints your progress.

**I press `Save and continue` and the next window does not open.**
Either the operation you chose from the drop-down menu is not yet implemented, or something entered in the previous window broke the next one. Go back and check the previous window's inputs.

**The program seems permanently stuck.**
It is always safe to delete `parameters.txt` in the `Simple_RIXS_parameters/` subfolder. On the next run, fresh default parameters are generated automatically.

To avoid re-entering everything after a reset, choose `Replot treated spectra` from the drop-down menu and select an old treated file that worked. This loads that file's parameters over the defaults.

---

## Output files

Every operation saves its results into `<project_folder>/Simple_RIXS_figures/`. Three files are written per result:

| File | Contents |
|---|---|
| `<name>_data.txt` | Tab-separated columns of x values and intensities |
| `<name>_parameters.txt` | JSON record of all settings used to produce the result |
| `<name>_figure.png` | The matplotlib figure as a PNG image |

The `_parameters.txt` file means you can always trace back exactly what settings produced a given output, and re-run with the same settings later.

---

## Repository structure

```
Simple_RIXS.py                               # Template entry point — copy and rename per beamtime
simple_RIXS_main_logic.py                    # Main orchestrator, branches on the operation selected in the GUI
main_GUI_script.py                           # First dialog: choose what operation to perform
parameter_scripts.py                         # Load and save the parameters dictionary (JSON, .txt extension)
input_raw_data_information_script.py         # Generic raw file input dialog
input_veritas_file_information_script.py     # Veritas / Species specific input dialog
input_spring_8_file_information_script.py    # SPring-8 specific input dialog
find_elastic_peak_center.py                  # Elastic peak alignment dialog (generic)
find_elastic_peak_center_spring_8.py         # Elastic peak alignment dialog (SPring-8)
find_elastic_peak_center_galaxies.py         # Elastic peak alignment dialog (Galaxies)
make_treated_RIXS_script_2.py               # Convert generic raw data to treated RIXS files
make_treated_veritas_RIXS_script.py         # Convert Veritas raw data to treated RIXS files
make_treated_species_RIXS_script.py         # Convert Species raw data to treated RIXS files
make_treated_spring_8_RIXS_script.py        # Convert SPring-8 raw data to treated RIXS files
make_treated_galaxies_RIXS_script.py        # Convert Galaxies raw data to treated RIXS files
make_treated_XAS_script.py                  # Convert generic raw data to treated XAS files
make_treated_XAS_script_for_veritas.py      # Convert Veritas raw data to treated XAS files
make_treated_XAS_script_for_species.py      # Convert Species raw data to treated XAS files
veritas_time_resolved_RIXS_script.py        # Time-resolved RIXS analysis for Veritas DLD data
add_multiple_RIXS_spectra_to_waterfall.py   # Waterfall plot of multiple RIXS spectra
add_multiple_XAS_to_waterfall.py            # Waterfall plot of multiple XAS spectra
add_RIXS_map_intensities.py                 # Extract and compare intensity values from RIXS maps
make_PFY_spectra_from_several_treated_files.py  # PFY extraction
subtract_treated_files_script_2.py          # Subtract two treated line scans
subtract_treated_RIXS_maps_script.py        # Subtract two treated RIXS maps
select_*.py                                 # File browser dialogs for selecting treated files
plot_treated_spectra.py                     # Plot a single treated spectrum
```

---

## Per-facility notes

**Veritas and Species (MAX IV):** Raw data is stored in HDF5 files produced by the DLD (delay-line detector). Set `input_file_format` to `h5` in the GUI. For time-resolved measurements, use the "Treat Veritas raw data using time information" option, which divides the measurement into time windows based on the actual event timestamps recorded by the detector.

**SPring-8 BL27SU:** Raw data comes in facility-specific HDF5 files. Use the "Make treated RIXS data from SPring-8 BL27SU" option. The energy calibration can either be read from the file directly or entered manually as eV-per-channel and intercept values.

**SOLEIL Galaxies:** Uses a combination of text and HDF5 formats depending on the measurement. The detector pixel range can be selected interactively in a plot window before processing.

**Generic (ALS, Diamond, other facilities):** Use "Make treated RIXS data" for text or HDF5 files that follow a general column format. The elastic peak position is found interactively by clicking on a plot.

**NanoTerasu BL02U:** Support is experimental. Standalone test scripts are provided in the repository but the full GUI integration is not yet complete.

---

## Settings persistence

All settings are saved between runs in `<project_folder>/Simple_RIXS_parameters/parameters.txt`. This file uses JSON format despite the `.txt` extension. You do not need to manage this file manually — the program reads and writes it automatically. Any settings that are missing from an older file are backfilled from defaults when the program starts.

---

## Status

Simple RIXS was developed during doctoral work at Uppsala University
and is released as-is. It is not actively maintained, and I do not
expect to respond to issues or pull requests after 2027.

You are welcome to fork it and adapt it to your own beamline or
workflow — that is what the MIT license is for. If you extend it in
a way others would find useful, feel free to publish your fork.

---

## License

MIT License — see `LICENSE` for details.

---

## Citation

If you use Simple RIXS in published work, please acknowledge it as:

> Törnblom, P. *Simple RIXS* (2025). GitHub: https://github.com/pontustornblom/Simple_RIXS