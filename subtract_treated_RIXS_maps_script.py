#subtract_treated_rixs_maps_script

import sys
import os
import platform
import subprocess
from PyQt5.QtWidgets import (
    QLabel, QMainWindow, QCheckBox, QComboBox, QLineEdit, QPushButton,
    QLayout, QApplication, QVBoxLayout, QHBoxLayout, QWidget, QDesktopWidget,
    QTextEdit, QMessageBox, QScrollArea
)
from math import floor, ceil
import numpy as np
from PyQt5.QtCore import QEventLoop, pyqtSignal
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import matplotlib.colors as mcolors
from matplotlib.colors import Normalize
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
import json

import parameter_scripts
import create_complete_file_location_for_treated_data
import get_treated_rixs_data_script
import adjust_excitation_energy_for_pcolormesh_plot_script
import smoothing_scripts


# ============================================================
# Helper functions
# ============================================================

def nested_array_contains_negative_floats(nested_array):
    for array in nested_array:
        if np.any(np.asarray(array) < 0):
            return True
    return False


def ensure_emission_energy_scale(array_of_x_value_arrays, incoming_energy_array):
    x_copy = [np.copy(np.asarray(x)) for x in array_of_x_value_arrays]
    if nested_array_contains_negative_floats(x_copy):
        for idx in range(len(x_copy)):
            x_copy[idx] = x_copy[idx] + incoming_energy_array[idx]
    return x_copy


def ensure_energy_loss_scale(array_of_x_value_arrays, incoming_energy_array):
    x_copy = [np.copy(np.asarray(x)) for x in array_of_x_value_arrays]
    if not nested_array_contains_negative_floats(x_copy):
        for idx in range(len(x_copy)):
            x_copy[idx] = x_copy[idx] - incoming_energy_array[idx]
    return x_copy


def match_excitation_energies(incoming_1, incoming_2, tolerance=0.05):
    matched_indices = []
    matched_energies = []
    used_j = set()
    for i, e1 in enumerate(incoming_1):
        best_j = None
        best_diff = tolerance + 1
        for j, e2 in enumerate(incoming_2):
            if j in used_j:
                continue
            diff = abs(e1 - e2)
            if diff < best_diff:
                best_diff = diff
                best_j = j
        if best_j is not None and best_diff <= tolerance:
            matched_indices.append((i, best_j))
            matched_energies.append(0.5 * (e1 + incoming_2[best_j]))
            used_j.add(best_j)
    return matched_indices, np.array(matched_energies)


def compute_normalization_factor_in_region(
    array_of_x_value_arrays, incoming_energy_array,
    array_of_intensity_arrays,
    excitation_min, excitation_max,
    x_min, x_max
):
    total = 0.0
    n_pts = 0
    for i, e_in in enumerate(incoming_energy_array):
        if e_in < excitation_min or e_in > excitation_max:
            continue
        x = np.asarray(array_of_x_value_arrays[i])
        y = np.asarray(array_of_intensity_arrays[i])
        mask = (x >= x_min) & (x <= x_max)
        if not np.any(mask):
            continue
        total += np.sum(y[mask])
        n_pts += int(np.sum(mask))
    avg = total / n_pts if n_pts > 0 else np.nan
    return total, n_pts, avg


# ============================================================
# Main GUI
# ============================================================

def run_main_gui(parameters):
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    main_window = MainWindow(parameters)
    main_window.show()
    loop = QEventLoop()
    main_window.finished.connect(loop.quit)
    loop.exec_()
    parameters = main_window.get_inputted_parameters_from_gui()
    return parameters


class MainWindow(QMainWindow):
    finished = pyqtSignal()

    def __init__(self, parameters):
        super().__init__()
        self.parameters = parameters
        self.initUI()

    # --------------------------------------------------------
    # GUI construction
    # --------------------------------------------------------
    def initUI(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        self.setMinimumWidth(floor(screen_geometry.width() / 2 - 20))
        self.setFixedHeight(floor(screen_geometry.height() - floor(screen_geometry.height() / 9)))
        self.move(floor(screen_geometry.width() / 2 + 10), 10)

        self.vbox = QVBoxLayout()

        self.vbox.addLayout(self._label("input_file_project_folder", "Project folder:"))
        self.vbox.addLayout(self._label("input_file_raw_data_folder", "Raw-data subfolder:"))
        self.vbox.addLayout(self._button("open file location", "Open raw data folder"))
        self.vbox.addLayout(self._button("Update the plot", "Update the plot"))
        self.vbox.addLayout(self._create_bottom_buttons())

        self.vbox.addLayout(self._text("The following inputs only affect the saved file name"))
        self.vbox.addLayout(self._label("output_file_element", "Element:"))
        self.vbox.addLayout(self._combo("output_file_edge", "Edge:", [
            "K-edge", "L-edge", "L1-edge", "L2-edge", "L3-edge",
            "M-edge", "M1-edge", "M5-edge"]))
        self.vbox.addLayout(self._label("output_file_additional_comment", "Additional comment:"))

        self.vbox.addLayout(self._label("plot_figure_size_x_array_0", "Figure width (inches):"))
        self.vbox.addLayout(self._label("plot_figure_size_y_array_0", "Figure height (inches):"))
        self.vbox.addLayout(self._combo("plot_colormap_choice",
                                        "Colormap for map 1 and map 2:",
                                        ["turbo", "viridis", "gist_earth", "gist_stern",
                                         "inferno", "plasma", "gray", "gnuplot", "gist_rainbow"]))

        self.vbox.addLayout(self._label("plot_x_axis_text_size", "X-axis label size:"))
        self.vbox.addLayout(self._label("plot_y_axis_text_size", "Y-axis label size:"))
        self.vbox.addLayout(self._label("plot_x_axis_number_size", "X-axis tick size:"))
        self.vbox.addLayout(self._label("plot_y_axis_number_size", "Y-axis tick size:"))

        self.vbox.addLayout(self._check("plot_display_sample_name_title", "Display plot title?"))
        self.vbox.addLayout(self._label("plot_title", "Plot title:"))
        self.vbox.addLayout(self._label("plot_title_size", "Title font size:"))

        self.vbox.addLayout(self._check(
            "subtract_spectra_on_emission_energy_axis_instead_of_energy_loss",
            "Subtract on emission-energy axis (instead of energy loss)?"))
        self.vbox.addLayout(self._check(
            "plot_outgoing_energy_instead_of_energy_loss",
            "Plot final maps on emission-energy axis?"))

        self.vbox.addLayout(self._label(
            "energy_mismatch_tolerance",
            "Excitation-energy matching tolerance (eV):"))

        self._add_dynamic_checkbox(
            key="is_energy_window_used_array_0",
            label_text="Limit x-axis range?",
            child_specs=[
                ("label", "plot_energy_loss_min_array_0", "X-axis min:"),
                ("label", "plot_energy_loss_max_array_0", "X-axis max:"),
            ])

        # Color-scale for map 1 and map 2
        self._add_dynamic_checkbox(
            key="is_plot_intensity_limits_used_array_0",
            label_text="Limit color-scale range for map 1 and map 2?",
            child_specs=[
                ("label", "plot_intensity_min_array_0", "Color min:"),
                ("label", "plot_intensity_max_array_0", "Color max:"),
            ])

        # Color-scale for the difference map
        self._add_dynamic_checkbox(
            key="is_plot_difference_intensity_limits_used",
            label_text="Limit color-scale range for the difference map?",
            child_specs=[
                ("label", "plot_difference_intensity_min",
                 "Difference color min:"),
                ("label", "plot_difference_intensity_max",
                 "Difference color max:"),
            ])

        self.vbox.addLayout(self._text(
            "--- Regional intensity normalization (before subtraction) ---"))
        self._add_dynamic_checkbox(
            key="is_normalize_maps_in_region",
            label_text="Normalize both maps to average intensity = 1 in a region?",
            child_specs=[
                ("combo", "normalization_region_energy_scale",
                 "Energy scale for the normalization region:",
                 ["Emission energy", "Energy loss"]),
                ("label", "normalization_excitation_min",
                 "Normalization region — excitation energy min (eV):"),
                ("label", "normalization_excitation_max",
                 "Normalization region — excitation energy max (eV):"),
                ("label", "normalization_x_min",
                 "Normalization region — x-axis min (eV):"),
                ("label", "normalization_x_max",
                 "Normalization region — x-axis max (eV):"),
            ])

        self._add_dynamic_checkbox(
            key="is_gaussian_smooth_data_for_all_spectra",
            label_text="Gaussian-smooth all spectra before subtraction?",
            child_specs=[
                ("label", "sigma_for_gaussian_smoothing_array_0", "Gaussian sigma:"),
            ])

        self._add_dynamic_checkbox(
            key="is_binning_smooth_data_for_all_spectra",
            label_text="Bin data points before subtraction?",
            child_specs=[
                ("label", "number_of_bins_for_smoothing_array_0", "Number of points to bin:"),
            ])

        for file_idx in range(2):
            name = self.parameters["plot_legend_names_array"][file_idx]
            self.vbox.addLayout(self._text(
                f"------------ File {file_idx + 1}: {name} ------------"))
            self.vbox.addLayout(self._check(
                f"plot_is_scale_intensity_of_spectra_array_{file_idx}",
                "Scale intensity of this map?"))
            self.vbox.addLayout(self._label(
                f"plot_scaling_array_{file_idx}",
                "Intensity scale factor:"))

        self.vbox.addLayout(self._button("Update the plot", "Update the plot"))
        self.vbox.addLayout(self._text(
            "If everything looks good, hit 'Continue' to proceed to the difference map editor."))
        self.vbox.addLayout(self._create_bottom_buttons())

        central = QWidget()
        central.setLayout(self.vbox)
        scroll = QScrollArea()
        scroll.setWidget(central)
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)
        self.setWindowTitle("RIXS map subtraction")
        self.show()
        self.do_plot()

    # ------------------------------------------------------------------
    # Dynamic checkbox
    # ------------------------------------------------------------------
    def _add_dynamic_checkbox(self, key, label_text, child_specs):
        hbox = self._check(key, label_text)
        self.vbox.addLayout(hbox)

        if "array" in key:
            parts = key.split('_')
            array_key = '_'.join(parts[:-1])
            array_index = int(parts[-1])
            initially_checked = bool(self.parameters.get(array_key, [False])[array_index])
        else:
            initially_checked = bool(self.parameters.get(key, False))

        state_attr = "_dynamic_children_" + key.replace(" ", "_")
        setattr(self, state_attr, 0)

        def _toggle(checked, hbox_ref=hbox, specs=child_specs, sattr=state_attr):
            current_count = getattr(self, sattr)
            parent_pos = self.vbox.indexOf(hbox_ref)
            if checked:
                for offset, spec in enumerate(specs):
                    if spec[0] == "label":
                        child = self._label(spec[1], spec[2])
                    elif spec[0] == "combo":
                        child = self._combo(spec[1], spec[2], spec[3])
                    elif spec[0] == "check":
                        child = self._check(spec[1], spec[2])
                    else:
                        continue
                    self.vbox.insertLayout(parent_pos + 1 + offset, child)
                setattr(self, sattr, len(specs))
            else:
                for _ in range(current_count):
                    self._remove_item_at(parent_pos + 1)
                setattr(self, sattr, 0)

        for i in range(hbox.count()):
            widget = hbox.itemAt(i).widget()
            if isinstance(widget, QCheckBox):
                widget.clicked.connect(_toggle)
                break

        if initially_checked:
            _toggle(True)

    # ------------------------------------------------------------------
    # GUI-item helpers
    # ------------------------------------------------------------------
    def _label(self, key, text):
        return self._gui(key, text, "q_line_edit", [""])

    def _check(self, key, text):
        return self._gui(key, text, "q_check_box", [""])

    def _combo(self, key, text, options):
        return self._gui(key, text, "q_combo_box", options)

    def _button(self, key, text):
        return self._gui(key, text, "q_push_button", [""])

    def _text(self, text):
        return self._gui("", text, "q_text_label", [""])

    def _gui(self, key, item_label_text, item_type, combo_box_options):
        hbox = QHBoxLayout()
        label = QLabel(item_label_text)

        if item_type == "q_line_edit":
            hbox.addWidget(label)
            if "array" in key:
                parts = key.split('_')
                array_key = '_'.join(parts[:-1])
                array_index = int(parts[-1])
                while len(self.parameters.get(array_key, [])) <= array_index:
                    self.parameters[array_key].append(self.parameters[array_key][0])
                item = QLineEdit(str(self.parameters[array_key][array_index]))
                hbox.addWidget(item)
                item.editingFinished.connect(
                    lambda ak=array_key, ai=array_index, it=item:
                        self._set_array(ak, ai, it.text()))
            else:
                item = QLineEdit(str(self.parameters.get(key, "")))
                hbox.addWidget(item)
                item.textChanged.connect(lambda text, k=key: self._set(k, text))

        elif item_type == "q_combo_box":
            hbox.addWidget(label)
            item = QComboBox()
            item.addItems(combo_box_options)
            if "array" in key:
                parts = key.split('_')
                array_key = '_'.join(parts[:-1])
                array_index = int(parts[-1])
                while len(self.parameters.get(array_key, [])) <= array_index:
                    self.parameters[array_key].append(self.parameters[array_key][0])
                item.setCurrentText(str(self.parameters[array_key][array_index]))
                hbox.addWidget(item)
                item.currentTextChanged.connect(
                    lambda text, ak=array_key, ai=array_index:
                        self._set_array_val(ak, ai, text))
            else:
                item.setCurrentText(str(self.parameters.get(key, "")))
                hbox.addWidget(item)
                item.currentTextChanged.connect(
                    lambda text, k=key: self._set(k, text))

        elif item_type == "q_check_box":
            hbox.addWidget(label)
            item = QCheckBox()
            if "array" in key:
                parts = key.split('_')
                array_key = '_'.join(parts[:-1])
                array_index = int(parts[-1])
                while len(self.parameters.get(array_key, [])) <= array_index:
                    self.parameters[array_key].append(self.parameters[array_key][0])
                item.setChecked(bool(self.parameters[array_key][array_index]))
                hbox.addWidget(item)
                item.clicked.connect(
                    lambda checked, ak=array_key, ai=array_index, it=item:
                        self._set_array_val(ak, ai, it.isChecked()))
            else:
                item.setChecked(bool(self.parameters.get(key, False)))
                hbox.addWidget(item)
                item.clicked.connect(
                    lambda checked, k=key, it=item:
                        self._set(k, it.isChecked()))

        elif item_type == "q_push_button":
            hbox.addWidget(QLabel(""))
            item = QPushButton(item_label_text)
            hbox.addWidget(item)
            if key == "open file location":
                item.clicked.connect(lambda: self._open_folder())
            elif key == "Update the plot":
                item.clicked.connect(lambda: self.do_plot())

        elif item_type == "q_text_label":
            hbox.addWidget(label)

        return hbox

    def _set(self, key, value):
        self.parameters[key] = value

    def _set_array(self, key, idx, text):
        self.parameters[key][idx] = text

    def _set_array_val(self, key, idx, value):
        self.parameters[key][idx] = value

    def _remove_item_at(self, index):
        item = self.vbox.itemAt(index)
        if item is None:
            return
        layout = item.layout()
        if layout is not None:
            self._delete_layout_contents(layout)
            self.vbox.removeItem(item)

    @staticmethod
    def _delete_layout_contents(layout):
        if layout is None:
            return
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                MainWindow._delete_layout_contents(child.layout())

    def _open_folder(self):
        folder = os.path.join(
            self.parameters["input_file_project_folder"],
            self.parameters["input_file_raw_data_folder"])
        if platform.system() == "Darwin":
            subprocess.call(["open", folder])
        else:
            subprocess.call(["explorer", folder])

    def _create_bottom_buttons(self):
        hbox = QHBoxLayout()
        for label, slot in [("Continue", self._continue),
                            ("Close", self._close)]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            hbox.addWidget(btn)
        hbox.setSpacing(50)
        hbox.setSizeConstraint(QLayout.SetFixedSize)
        return hbox

    def _continue(self):
        parameter_scripts.save_parameters(self.parameters)
        plt.close('all')
        self.finished.emit()
        self.close()

    def _close(self):
        self.parameters["is_program_running"] = False
        plt.close('all')
        self.finished.emit()
        self.close()

    def get_inputted_parameters_from_gui(self):
        return self.parameters

    # --------------------------------------------------------
    # Core: load, match, normalize, subtract, plot
    # --------------------------------------------------------
    def do_plot(self):
        plt.close('all')
        p = self.parameters

        # --- Load both RIXS maps ---
        map_data = []
        for file_idx in range(2):
            loc = create_complete_file_location_for_treated_data \
                .create_complete_file_location_for_treated_data(
                    p["input_file_project_folder"],
                    p["input_complete_file_name_array"][file_idx])
            x_arrs, inc_arr, y_arrs = \
                get_treated_rixs_data_script.get_treated_rixs_data(loc)
            x_arrs = [np.asarray(x, dtype=float) for x in x_arrs]
            y_arrs = [np.asarray(y, dtype=float) for y in y_arrs]
            inc_arr = np.asarray(inc_arr, dtype=float)
            map_data.append((x_arrs, inc_arr, y_arrs))

        x1, inc1, y1 = map_data[0]
        x2, inc2, y2 = map_data[1]

        # --- Match excitation energies ---
        tol = float(p.get("energy_mismatch_tolerance", "0.05"))
        matched_idx, matched_E_in = match_excitation_energies(inc1, inc2, tolerance=tol)

        if len(matched_idx) == 0:
            QMessageBox.warning(self, "No match",
                                f"No excitation energies matched (tolerance = {tol} eV).")
            return

        n_matched = len(matched_idx)
        print(f"Matched {n_matched} excitation energies.")

        # --- Subtraction energy scale ---
        subtract_on_emission = bool(p.get(
            "subtract_spectra_on_emission_energy_axis_instead_of_energy_loss", False))

        if subtract_on_emission:
            x1_work = ensure_emission_energy_scale(x1, inc1)
            x2_work = ensure_emission_energy_scale(x2, inc2)
        else:
            x1_work = ensure_energy_loss_scale(x1, inc1)
            x2_work = ensure_energy_loss_scale(x2, inc2)

        y1_work = [np.copy(y) for y in y1]
        y2_work = [np.copy(y) for y in y2]

        # --- Smoothing ---
        if p.get("is_gaussian_smooth_data_for_all_spectra", False):
            sigma = float(p["sigma_for_gaussian_smoothing_array"][0])
            for i in range(len(y1_work)):
                y1_work[i] = gaussian_filter1d(y1_work[i], sigma)
            for i in range(len(y2_work)):
                y2_work[i] = gaussian_filter1d(y2_work[i], sigma)

        if p.get("is_binning_smooth_data_for_all_spectra", False):
            n_bin = int(p["number_of_bins_for_smoothing_array"][0])
            for i in range(len(y1_work)):
                y1_work[i] = smoothing_scripts.bin_intensity_array(y1_work[i], n_bin)
                x1_work[i] = smoothing_scripts.bin_energy_array(x1_work[i], n_bin)
            for i in range(len(y2_work)):
                y2_work[i] = smoothing_scripts.bin_intensity_array(y2_work[i], n_bin)
                x2_work[i] = smoothing_scripts.bin_energy_array(x2_work[i], n_bin)

        # --- Per-file intensity scaling ---
        for file_idx, y_work in enumerate([y1_work, y2_work]):
            if p["plot_is_scale_intensity_of_spectra_array"][file_idx]:
                factor = float(p["plot_scaling_array"][file_idx])
                for i in range(len(y_work)):
                    y_work[i] = y_work[i] * factor

        # --- Regional normalization: both maps normalized to avg = 1 in ROI ---
        if p.get("is_normalize_maps_in_region", False):
            norm_scale = p.get("normalization_region_energy_scale", "Emission energy")
            exc_min = float(p["normalization_excitation_min"])
            exc_max = float(p["normalization_excitation_max"])
            x_roi_min = float(p["normalization_x_min"])
            x_roi_max = float(p["normalization_x_max"])

            if norm_scale == "Emission energy":
                x1_norm = ensure_emission_energy_scale(x1, inc1)
                x2_norm = ensure_emission_energy_scale(x2, inc2)
            else:
                x1_norm = ensure_energy_loss_scale(x1, inc1)
                x2_norm = ensure_energy_loss_scale(x2, inc2)

            if p.get("is_binning_smooth_data_for_all_spectra", False):
                n_bin = int(p["number_of_bins_for_smoothing_array"][0])
                for i in range(len(x1_norm)):
                    x1_norm[i] = smoothing_scripts.bin_energy_array(x1_norm[i], n_bin)
                for i in range(len(x2_norm)):
                    x2_norm[i] = smoothing_scripts.bin_energy_array(x2_norm[i], n_bin)

            _, _, avg1 = compute_normalization_factor_in_region(
                x1_norm, inc1, y1_work, exc_min, exc_max, x_roi_min, x_roi_max)
            _, _, avg2 = compute_normalization_factor_in_region(
                x2_norm, inc2, y2_work, exc_min, exc_max, x_roi_min, x_roi_max)

            if np.isnan(avg1) or np.isnan(avg2):
                QMessageBox.warning(self, "Normalization",
                                    "No data in normalization region. Skipping.")
            elif avg1 == 0 or avg2 == 0:
                QMessageBox.warning(self, "Normalization",
                                    "Zero average in normalization region. Skipping.")
            else:
                # Normalize BOTH maps so the average in the ROI becomes 1
                print(f"Regional normalization: map 1 avg = {avg1:.6e}, "
                      f"map 2 avg = {avg2:.6e}")
                print(f"  Scaling map 1 by 1/{avg1:.6e} = {1.0/avg1:.6e}")
                print(f"  Scaling map 2 by 1/{avg2:.6e} = {1.0/avg2:.6e}")
                for i in range(len(y1_work)):
                    y1_work[i] = y1_work[i] / avg1
                for i in range(len(y2_work)):
                    y2_work[i] = y2_work[i] / avg2

        # --- Interpolate & subtract per matched pair ---
        map1_x_arrays = []
        map2_x_arrays = []
        diff_x_arrays = []
        map1_y_arrays = []
        map2_y_arrays = []
        diff_y_arrays = []

        for i1, i2 in matched_idx:
            x_a, x_b = x1_work[i1], x2_work[i2]
            overlap_lo = max(np.min(x_a), np.min(x_b))
            overlap_hi = min(np.max(x_a), np.max(x_b))
            if overlap_lo >= overlap_hi:
                continue

            n_pts = min(len(x_a), len(x_b))
            x_common = np.linspace(overlap_lo, overlap_hi, max(n_pts, 50))

            f1 = interp1d(x_a, y1_work[i1], kind='linear',
                          bounds_error=False, fill_value=0.0)
            f2 = interp1d(x_b, y2_work[i2], kind='linear',
                          bounds_error=False, fill_value=0.0)
            y1_interp = f1(x_common)
            y2_interp = f2(x_common)

            map1_x_arrays.append(np.copy(x_common))
            map2_x_arrays.append(np.copy(x_common))
            diff_x_arrays.append(np.copy(x_common))
            map1_y_arrays.append(y1_interp)
            map2_y_arrays.append(y2_interp)
            diff_y_arrays.append(y1_interp - y2_interp)

        if len(diff_y_arrays) == 0:
            QMessageBox.warning(self, "No overlap",
                                "The two maps have no overlapping x-axis range.")
            return

        # Keep only matched energies for pairs that had overlap
        valid_matched_E_in = []
        for pair_idx, (i1, i2) in enumerate(matched_idx):
            x_a, x_b = x1_work[i1], x2_work[i2]
            if max(np.min(x_a), np.min(x_b)) < min(np.max(x_a), np.max(x_b)):
                valid_matched_E_in.append(matched_E_in[pair_idx])
        matched_E_in = np.array(valid_matched_E_in)

        # --- Convert x-arrays to the final plot scale ---
        plot_on_emission = bool(p.get("plot_outgoing_energy_instead_of_energy_loss", False))

        def convert_x_arrays_for_plot(x_arrays):
            result = []
            for row_idx, x in enumerate(x_arrays):
                x_out = np.copy(x)
                if plot_on_emission and not subtract_on_emission:
                    x_out = x_out + matched_E_in[row_idx]
                elif not plot_on_emission and subtract_on_emission:
                    x_out = x_out - matched_E_in[row_idx]
                result.append(x_out)
            return result

        plot_map1_x = convert_x_arrays_for_plot(map1_x_arrays)
        plot_map2_x = convert_x_arrays_for_plot(map2_x_arrays)
        plot_diff_x = convert_x_arrays_for_plot(diff_x_arrays)

        if plot_on_emission:
            x_label = "Emission energy [eV]"
        else:
            x_label = "Energy loss [eV]"

        # --- Store for saving ---
        self.plot_diff_x = plot_diff_x
        self.matched_E_in = matched_E_in
        self.map1_y_arrays = map1_y_arrays
        self.map2_y_arrays = map2_y_arrays
        self.diff_y_arrays = diff_y_arrays

        # --- Plot with pcolormesh ---
        fig_w = float(p["plot_figure_size_x_array"][0])
        fig_h = float(p["plot_figure_size_y_array"][0])
        self.figure_to_save, (ax1, ax2, ax3) = plt.subplots(
            1, 3, figsize=(fig_w, fig_h), constrained_layout=True)

        inc_edges = adjust_excitation_energy_for_pcolormesh_plot_script \
            .adjust_excitation_energy_for_pcolormesh_plot(matched_E_in)

        # Shared intensity range for map1 and map2
        all_map1 = np.concatenate(map1_y_arrays)
        all_map2 = np.concatenate(map2_y_arrays)
        vmin_shared = min(np.min(all_map1), np.min(all_map2))
        vmax_shared = max(np.max(all_map1), np.max(all_map2))

        if p["is_plot_intensity_limits_used_array"][0]:
            vmin_shared = float(p["plot_intensity_min_array"][0])
            vmax_shared = float(p["plot_intensity_max_array"][0])

        norm_shared = Normalize(vmin=vmin_shared, vmax=vmax_shared)
        cmap = p.get("plot_colormap_choice", "turbo")

        # Difference map norm: user-specified or CenteredNorm
        if p.get("is_plot_difference_intensity_limits_used", False):
            diff_vmin = float(p["plot_difference_intensity_min"])
            diff_vmax = float(p["plot_difference_intensity_max"])
            diff_norm = Normalize(vmin=diff_vmin, vmax=diff_vmax)
        else:
            diff_norm = mcolors.CenteredNorm()

        def plot_map(ax, x_arrays, y_arrays, norm_to_use, cmap_to_use):
            im = None
            for row_idx in range(len(y_arrays)):
                x_edges = adjust_excitation_energy_for_pcolormesh_plot_script \
                    .adjust_excitation_energy_for_pcolormesh_plot(x_arrays[row_idx])
                im = ax.pcolormesh(
                    x_edges,
                    inc_edges[row_idx: row_idx + 2],
                    [y_arrays[row_idx]],
                    cmap=cmap_to_use,
                    shading='flat',
                    norm=norm_to_use
                )
            return im

        # Map 1
        im1 = plot_map(ax1, plot_map1_x, map1_y_arrays, norm_shared, cmap)
        ax1.set_title(p["plot_legend_names_array"][0],
                      fontsize=float(p.get("plot_title_size", 14)))
        ax1.set_xlabel(x_label, fontsize=float(p["plot_x_axis_text_size"]))
        ax1.set_ylabel("Excitation energy [eV]", fontsize=float(p["plot_y_axis_text_size"]))

        # Map 2
        im2 = plot_map(ax2, plot_map2_x, map2_y_arrays, norm_shared, cmap)
        ax2.set_title(p["plot_legend_names_array"][1],
                      fontsize=float(p.get("plot_title_size", 14)))
        ax2.set_xlabel(x_label, fontsize=float(p["plot_x_axis_text_size"]))
        ax2.set_ylabel("")

        # Difference map
        im3 = plot_map(ax3, plot_diff_x, diff_y_arrays, diff_norm, 'bwr')
        diff_title = (f"{p['plot_legend_names_array'][0]}  −  "
                      f"{p['plot_legend_names_array'][1]}")
        ax3.set_title(diff_title, fontsize=float(p.get("plot_title_size", 14)))
        ax3.set_xlabel(x_label, fontsize=float(p["plot_x_axis_text_size"]))
        ax3.set_ylabel("")

        # Colorbars
        if im1 is not None:
            self.figure_to_save.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
        if im2 is not None:
            self.figure_to_save.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
        if im3 is not None:
            cbar3 = self.figure_to_save.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)
            cbar3.set_label('Difference', fontsize=12)

        # Axis limits
        if p["is_energy_window_used_array"][0]:
            for ax in (ax1, ax2, ax3):
                ax.set_xlim(float(p["plot_energy_loss_min_array"][0]),
                            float(p["plot_energy_loss_max_array"][0]))

        for ax in (ax1, ax2, ax3):
            ax.minorticks_on()
            ax.xaxis.set_tick_params(labelsize=float(p["plot_x_axis_number_size"]))
            ax.yaxis.set_tick_params(labelsize=float(p["plot_y_axis_number_size"]))

        if p.get("plot_display_sample_name_title", False):
            self.figure_to_save.suptitle(p["plot_title"],
                                         fontsize=float(p.get("plot_title_size", 16)))

        self.figure_to_save.show()



# ============================================================
# Entry point
# ============================================================
if __name__ == '__main__':
    input_file_location = (
        r"C:\Users\ponto479\Documents\02 Beamtime Data"
        r"\pyrophosphate_P_L_edge_data\Simple RIXS Figures"
    )
    parameters = parameter_scripts.get_parameters(input_file_location)
    parameters = run_main_gui(parameters)