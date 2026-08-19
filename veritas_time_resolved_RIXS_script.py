#veritas_time_resolved_RIXS_script
import sys
import os
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from math import floor
from PyQt5.QtWidgets import (QLabel, QMainWindow, QComboBox, QLineEdit,
                              QPushButton, QLayout, QApplication, QVBoxLayout,
                              QHBoxLayout, QWidget, QDesktopWidget, QScrollArea)
from PyQt5.QtCore import QEventLoop, pyqtSignal
from scipy.ndimage import shift as ndimage_shift
from scipy.optimize import curve_fit
from PyQt5.QtWidgets import QCheckBox
import parameter_scripts
import json


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
        self._cache_key = None
        self._cached_points = None
        self._cached_emission_energy = None
        self._cached_detector_shift = None
        self._last_array_of_x_value_arrays = None
        self._last_array_of_intensity_arrays = None
        self._last_time_centers_minutes = None
        self.initUI()

    # ------------------------------------------------------------------
    def initUI(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        self.setMinimumWidth(floor(screen_geometry.width() / 2 - 20))
        self.setFixedHeight(floor(screen_geometry.height() - floor(screen_geometry.height() / 9)))
        self.move(floor(screen_geometry.width() / 2 + 10), 10)

        self.vbox = QVBoxLayout()

        self.vbox.addLayout(self.create_gui_item("input_file_project_folder",  "Project folder: ",                                  "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("input_file_raw_data_folder", "Raw data subfolder: ",                              "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("veritas_time_rixs_file_name","H5 file name: ",                                    "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("veritas_time_rixs_acquisition_number", "Acquisition number: ",                    "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("veritas_time_rixs_incoming_energy",    "Incoming (excitation) energy [eV]: ",     "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("veritas_time_rixs_plot_energy_type",   "Plot x-axis as: ",                        "q_combo_box", ["Emission energy", "Energy loss"]))

        self.vbox.addLayout(self.create_gui_item("", "--- Detector pixel range to include (y-axis of 2D detector) ---", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("veritas_time_rixs_y_pixel_start", "Y pixel start: ",  "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("veritas_time_rixs_y_pixel_end",   "Y pixel end: ",    "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("", "--- Elastic peak alignment ---", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("is_automatically_adjust_peak_to_correct_energy",
            "Automatically shift elastic peak to correct energy?\n"
            "(Squared-intensity weighted fit followed by Gaussian fit.) ",
            "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("energy_above_and_below_to_calculate_elastic_peak_weights",
            "Energy window above/below elastic peak for alignment fit [eV]: ",
            "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("", "--- Background subtraction ---", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("is_subtract_background_from_RIXS",
            "Set intensity to zero above the elastic peak? (Background subtraction) ",
            "q_check_box", [""]))
        self.vbox.addLayout(self.create_gui_item("energy_above_elastic_peak_to_fit_background_start",
            "eV above elastic peak — start of background averaging region: ",
            "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("energy_above_elastic_peak_to_fit_background_end",
            "eV above elastic peak — end of background averaging region: ",
            "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("", "--- Time-resolved extraction ---", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("veritas_time_rixs_start_time_minutes",     "Start time offset [minutes]: ",         "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("veritas_time_rixs_number_of_spectra",      "Number of spectra to extract: ",        "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("veritas_time_rixs_time_per_spectra_minutes","Integration time per spectrum [min]: ","q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("", "--- RIXS map settings ---", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("veritas_time_rixs_map_time_bins", "Number of time bins in the map: ", "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("plot_colormap_choice",             "Color map: ",                     "q_combo_box", ["turbo", "viridis", "plasma", "inferno", "magma", "hot", "coolwarm", "bwr"]))

        self.vbox.addLayout(self.create_gui_item("veritas_time_rixs_curvature_coeffs",
            "Detector curvature polynomial coefficients\n(comma-separated, highest degree first): ",
            "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("Update the plot", "Update the plot", "q_push_button", [""]))

        self.vbox.addLayout(self.create_gui_item("", "--- Output file name options ---", "q_text_label", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_element",            "Element: ",             "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_edge",               "Edge: ",                "q_combo_box", ["K-edge", "L-edge", "L1-edge", "L2-edge", "L3-edge", "M-edge", "M1-edge", "M5-edge"]))
        self.vbox.addLayout(self.create_gui_item("output_file_sample_name",        "Sample name: ",         "q_line_edit", [""]))
        self.vbox.addLayout(self.create_gui_item("output_file_additional_comment", "Additional comment: ",  "q_line_edit", [""]))

        self.vbox.addLayout(self.create_gui_item("", "If everything looks good click Save and continue to save the extracted spectra.", "q_text_label", [""]))
        self.vbox.addLayout(self.create_bottom_buttons())

        central_widget = QWidget()
        central_widget.setLayout(self.vbox)
        scroll = QScrollArea()
        scroll.setWidget(central_widget)
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)
        self.setWindowTitle("Simple RIXS — Treat Veritas raw data using time information")
        self.show()

        try:
            self._load_and_plot()
        except Exception as exc:
            print("Initial plot skipped:", exc)

    # ------------------------------------------------------------------
    def create_gui_item(self, key, label_text, item_type, combo_options):
        hbox = QHBoxLayout()
        label = QLabel(label_text)
        if item_type == "q_line_edit":
            hbox.addWidget(label)
            item = QLineEdit(self.parameters.get(key, ""))
            hbox.addWidget(item)
            item.textChanged.connect(lambda text, k=key: self.parameters.update({k: text}))
        elif item_type == "q_combo_box":
            hbox.addWidget(label)
            item = QComboBox()
            item.addItems(combo_options)
            item.setCurrentText(self.parameters.get(key, combo_options[0]))
            hbox.addWidget(item)
            item.currentTextChanged.connect(lambda text, k=key: self.parameters.update({k: text}))
        elif item_type == "q_check_box":
            hbox.addWidget(label)
            item = QCheckBox()
            item.setChecked(bool(self.parameters.get(key, False)))
            hbox.addWidget(item)
            item.clicked.connect(lambda checked, k=key: self.parameters.update({k: checked}))
        elif item_type == "q_push_button":
            label = QLabel("")
            hbox.addWidget(label)
            item = QPushButton(label_text)
            hbox.addWidget(item)
            if key == "Update the plot":
                item.clicked.connect(self._load_and_plot)
        elif item_type == "q_text_label":
            hbox.addWidget(label)
        return hbox

    # ------------------------------------------------------------------
    def create_bottom_buttons(self):
        save_continue = QPushButton("Save and Continue")
        save_close    = QPushButton("Save and Close")
        close_btn     = QPushButton("Close")
        save_continue.clicked.connect(self.save_and_continue)
        save_close.clicked.connect(self.save_and_close)
        close_btn.clicked.connect(self.close_program)
        hbox = QHBoxLayout()
        hbox.addWidget(save_continue)
        hbox.addWidget(save_close)
        hbox.addWidget(close_btn)
        hbox.setSpacing(50)
        hbox.setSizeConstraint(QLayout.SetFixedSize)
        return hbox

    # ------------------------------------------------------------------
    # Elastic peak helpers (adapted from make_treated_veritas_RIXS_script)
    # ------------------------------------------------------------------
    def _gaussian_with_offset(self, x, A, mu, sigma, offset):
        return A * np.exp(-(x - mu) ** 2 / (2 * sigma ** 2)) + offset

    def _nested_contains_negative(self, nested):
        for arr in nested:
            if np.any(np.asarray(arr) < 0):
                return True
        return False

    def _align_elastic_peaks(self, array_of_intensity_arrays, incoming_energy_array,
                              array_of_x_value_arrays):
        energy_above_and_below = float(
            self.parameters.get("energy_above_and_below_to_calculate_elastic_peak_weights", "1"))

        is_energy_loss = self._nested_contains_negative(array_of_x_value_arrays)
        if not is_energy_loss:
            for i in range(len(array_of_intensity_arrays)):
                array_of_x_value_arrays[i] = array_of_x_value_arrays[i] - incoming_energy_array[i]

        # Pass 1: converging squared-intensity weighted fit
        for si in range(len(array_of_intensity_arrays)):
            prev_ctr = int(np.abs(array_of_x_value_arrays[si] - 0).argmin())
            condition = True
            while condition:
                ch_above = int(np.abs(prev_ctr - np.abs(array_of_x_value_arrays[si] - energy_above_and_below).argmin()))
                ch_below = int(np.abs(prev_ctr - np.abs(array_of_x_value_arrays[si] + energy_above_and_below).argmin()))
                n = len(array_of_intensity_arrays[si])
                peak_e = 0.0; wsum = 0.0
                for ch in range(max(0, prev_ctr - ch_below), min(n, prev_ctr + ch_above + 1)):
                    w = float(array_of_intensity_arrays[si][ch]) ** 2
                    peak_e += w * array_of_x_value_arrays[si][ch]
                    wsum += w
                peak_e /= wsum if wsum > 0 else 1.0
                new_ctr = int(np.abs(array_of_x_value_arrays[si] - peak_e).argmin())
                change = prev_ctr - new_ctr
                prev_ctr = round(new_ctr)
                array_of_x_value_arrays[si] = array_of_x_value_arrays[si] - peak_e
                if abs(change) <= 0.5:
                    condition = False

        # Pass 2: half-width weighted fit → Gaussian for sub-channel precision
        for si in range(len(array_of_intensity_arrays)):
            prev_ctr = int(np.abs(array_of_x_value_arrays[si] - 0).argmin())
            ch_above = int(np.abs(prev_ctr - np.abs(array_of_x_value_arrays[si] - energy_above_and_below).argmin()))
            ch_below = int(np.abs(prev_ctr - np.abs(array_of_x_value_arrays[si] + energy_above_and_below).argmin()))

            # Refine center to intensity maximum in window
            n = len(array_of_intensity_arrays[si])
            s0 = max(0, prev_ctr - ch_above)
            s1 = min(n, prev_ctr + ch_above + 1)
            if s1 > s0:
                prev_ctr = s0 + int(np.argmax(array_of_intensity_arrays[si][s0:s1]))

            rough_half = (np.max(array_of_intensity_arrays[si][max(0, prev_ctr - ch_above):min(n, prev_ctr + ch_above + 1)])
                         - np.nanmin(array_of_intensity_arrays[si][prev_ctr:min(n, prev_ctr + 10 * ch_above + 1)])) / 2
            hw_ch = int(np.abs(array_of_intensity_arrays[si][prev_ctr:] - rough_half).argmin())
            if hw_ch <= 1:
                hw_ch = 2
            hw_energy = array_of_x_value_arrays[si][min(n - 1, prev_ctr + hw_ch)] - array_of_x_value_arrays[si][prev_ctr]

            condition = True; it = 0
            while condition:
                ch_above = int(np.abs(prev_ctr - np.abs(array_of_x_value_arrays[si] - hw_energy).argmin()))
                ch_below = int(np.abs(prev_ctr - np.abs(array_of_x_value_arrays[si] + hw_energy).argmin()))
                peak_e = 0.0; wsum = 0.0
                for ch in range(max(0, prev_ctr - ch_below), min(n, prev_ctr + ch_above + 1)):
                    w = float(array_of_intensity_arrays[si][ch]) ** 2
                    peak_e += w * array_of_x_value_arrays[si][ch]
                    wsum += w
                peak_e /= wsum if wsum > 0 else 1.0
                new_ctr = int(np.abs(array_of_x_value_arrays[si] - peak_e).argmin())
                change = prev_ctr - new_ctr
                prev_ctr = round(new_ctr)
                array_of_x_value_arrays[si] = array_of_x_value_arrays[si] - peak_e
                hw_ch = int(np.abs(array_of_intensity_arrays[si][prev_ctr:] - rough_half).argmin())
                if hw_ch <= 1:
                    hw_ch = 2
                hw_energy = array_of_x_value_arrays[si][min(n - 1, prev_ctr + hw_ch)] - array_of_x_value_arrays[si][prev_ctr]
                it += 1
                if abs(change) <= 0.5 or it >= 100:
                    condition = False

            # Gaussian fit for sub-channel precision
            try:
                prev_ctr = int(np.abs(array_of_x_value_arrays[si] - 0).argmin())
                FWHM = 2 * hw_energy
                fit_start = int(np.abs(array_of_x_value_arrays[si] + hw_energy / 2 * 1.05).argmin())
                fit_end   = min(n - 1, prev_ctr + 20 * hw_ch)
                x_g = array_of_x_value_arrays[si][fit_start:fit_end + 1]
                y_g = array_of_intensity_arrays[si][fit_start:fit_end + 1].astype(float)
                sigma_g = FWHM / 2.35482
                A_g = float(array_of_intensity_arrays[si][prev_ctr])
                off_g = float(np.mean(array_of_intensity_arrays[si][min(n - 1, prev_ctr + 15 * hw_ch):fit_end + 1]))
                gp, _ = curve_fit(self._gaussian_with_offset, x_g, y_g,
                                  p0=[A_g, array_of_x_value_arrays[si][prev_ctr], sigma_g, off_g])
                array_of_x_value_arrays[si] = array_of_x_value_arrays[si] - gp[1]
                print("  Spectra {}: Gaussian mu = {:.4f} eV".format(si, gp[1]))
            except RuntimeError:
                print("  Spectra {}: Gaussian fit failed, using weighted centroid.".format(si))

        if not is_energy_loss:
            for i in range(len(array_of_intensity_arrays)):
                array_of_x_value_arrays[i] = array_of_x_value_arrays[i] + incoming_energy_array[i]

        return array_of_x_value_arrays

    # ------------------------------------------------------------------
    def _subtract_background(self, array_of_intensity_arrays, incoming_energy_array,
                              array_of_x_value_arrays):
        start_ev = float(self.parameters.get("energy_above_elastic_peak_to_fit_background_start", "1"))
        end_ev   = float(self.parameters.get("energy_above_elastic_peak_to_fit_background_end",   "2"))
        is_energy_loss = self._nested_contains_negative(array_of_x_value_arrays)
        for si in range(len(array_of_intensity_arrays)):
            x = array_of_x_value_arrays[si]
            if is_energy_loss:
                ch0 = int(np.abs(x - start_ev).argmin())
                ch1 = int(np.abs(x - end_ev).argmin())
            else:
                ch0 = int(np.abs(x - incoming_energy_array[si] - start_ev).argmin())
                ch1 = int(np.abs(x - incoming_energy_array[si] - end_ev).argmin())
            if ch0 > ch1:
                ch0, ch1 = ch1, ch0
            if ch0 == ch1:
                bg = float(array_of_intensity_arrays[si][ch0])
            else:
                bg = float(np.mean(array_of_intensity_arrays[si][ch0:ch1]))
            array_of_intensity_arrays[si] = array_of_intensity_arrays[si] - bg
        return array_of_intensity_arrays

    # ------------------------------------------------------------------
    def _build_complete_file_location(self):
        p = self.parameters
        return os.path.join(p["input_file_project_folder"],
                            p["input_file_raw_data_folder"],
                            p["veritas_time_rixs_file_name"])

    def _parse_curvature_coeffs(self):
        raw = self.parameters.get("veritas_time_rixs_curvature_coeffs", "")
        try:
            parts = [float(x.strip()) for x in raw.split(",") if x.strip()]
            if len(parts) < 2:
                raise ValueError
            return parts
        except Exception:
            return [-0.0000033518618458794176, 0.012598028611163797, 1388.5048687275685]

    def _load_raw_data(self):
        p = self.parameters
        complete_file = self._build_complete_file_location()
        acq = int(p["veritas_time_rixs_acquisition_number"])
        cache_key = (complete_file, acq)
        if self._cache_key == cache_key:
            return  # already loaded

        print("Loading raw DLD data from:", complete_file)
        energy_root = f"acq{acq}/Instrument/DLD8080/calibration/energy_scale"
        points_root = f"acq{acq}/Instrument/DLD8080/data/points"

        with h5py.File(complete_file, 'r') as f:
            emission_energy = np.asarray(f[energy_root][:])
            raw_points      = np.asarray(f[points_root][:])

        # Sort by timestamp
        sort_idx = np.argsort(raw_points[:, 3].astype(np.int64))
        raw_points = raw_points[sort_idx]

        # Build curvature correction lookup
        y_all = np.arange(8192)
        coeffs = self._parse_curvature_coeffs()
        detector_shift = np.polyval(coeffs, y_all)

        self._cached_points         = raw_points
        self._cached_emission_energy = emission_energy
        self._cached_detector_shift  = detector_shift
        self._cache_key = cache_key
        print("Loaded {:,} events. Total time: {:.2f} min".format(
            len(raw_points),
            (raw_points[-1, 3] - raw_points[0, 3]) / 60.0))

    # ------------------------------------------------------------------
    def _compute_extracted_spectra(self):
        p = self.parameters
        raw_points       = self._cached_points
        emission_energy  = self._cached_emission_energy
        detector_shift   = self._cached_detector_shift

        n_spectra      = int(p["veritas_time_rixs_number_of_spectra"])
        t_per_min      = float(p["veritas_time_rixs_time_per_spectra_minutes"])
        start_min      = float(p.get("veritas_time_rixs_start_time_minutes", "0"))
        y_start        = int(p["veritas_time_rixs_y_pixel_start"])
        y_end          = int(p["veritas_time_rixs_y_pixel_end"])

        timestamps = raw_points[:, 3].astype(np.int64)
        t_min_abs  = timestamps[0]

        start_sec  = t_min_abs + int(start_min * 60)
        t_per_sec  = t_per_min * 60.0
        cuts_sec   = start_sec + np.arange(n_spectra + 1) * t_per_sec
        cut_idx    = np.searchsorted(timestamps, cuts_sec.astype(np.int64), side='left')

        n_channels = len(emission_energy)
        array_of_intensity_arrays = []
        time_centers_minutes = []

        for seg in range(n_spectra):
            i0, i1 = cut_idx[seg], cut_idx[seg + 1]
            seg_pts = raw_points[i0:i1]

            x_px = seg_pts[:, 0].astype(int)
            y_px = seg_pts[:, 1].astype(int)

            # Clamp to valid range
            valid = (x_px >= 0) & (x_px < 8192) & (y_px >= 0) & (y_px < 8192)
            x_px, y_px = x_px[valid], y_px[valid]

            # Build 2D grid and apply curvature correction
            grid = np.zeros((8192, 8192), dtype=np.float32)
            np.add.at(grid, (y_px, x_px), 1)

            grid_corrected = np.zeros_like(grid)
            for row_idx in range(grid.shape[0]):
                s = -detector_shift[row_idx]
                row = grid[row_idx, :]
                if not np.isnan(s) and s != 0:
                    grid_corrected[row_idx, :] = ndimage_shift(
                        row.astype(float), shift=s,
                        order=1, mode='constant', cval=0.0)
                else:
                    grid_corrected[row_idx, :] = row

            # Sum over y-pixel range
            mask = np.zeros(8192, dtype=bool)
            mask[y_start:y_end + 1] = True
            intensity = grid_corrected[mask, :].sum(axis=0)
            # Clip to valid energy channels
            intensity = intensity[:n_channels]

            array_of_intensity_arrays.append(intensity)
            t_center = start_min + (seg + 0.5) * t_per_min
            time_centers_minutes.append(t_center)
            print("  Segment {}: {:,} events".format(seg, i1 - i0))

        array_of_x_value_arrays = [emission_energy[:n_channels].copy()
                                    for _ in range(n_spectra)]
        incoming_energy_array = np.full(n_spectra, float(p["veritas_time_rixs_incoming_energy"]))

        if p.get("is_automatically_adjust_peak_to_correct_energy", False):
            print("Aligning elastic peaks …")
            array_of_x_value_arrays = self._align_elastic_peaks(
                array_of_intensity_arrays, incoming_energy_array, array_of_x_value_arrays)

        if p.get("is_subtract_background_from_RIXS", False):
            print("Subtracting background …")
            array_of_intensity_arrays = self._subtract_background(
                array_of_intensity_arrays, incoming_energy_array, array_of_x_value_arrays)

        self._last_array_of_x_value_arrays  = array_of_x_value_arrays
        self._last_array_of_intensity_arrays = array_of_intensity_arrays
        self._last_time_centers_minutes      = time_centers_minutes

    # ------------------------------------------------------------------
    def _build_rixs_map(self):
        p = self.parameters
        raw_points      = self._cached_points
        emission_energy = self._cached_emission_energy
        detector_shift  = self._cached_detector_shift

        n_map_bins  = int(p["veritas_time_rixs_map_time_bins"])
        y_start     = int(p["veritas_time_rixs_y_pixel_start"])
        y_end       = int(p["veritas_time_rixs_y_pixel_end"])
        start_min   = float(p.get("veritas_time_rixs_start_time_minutes", "0"))
        n_spectra   = int(p["veritas_time_rixs_number_of_spectra"])
        t_per_min   = float(p["veritas_time_rixs_time_per_spectra_minutes"])

        timestamps  = raw_points[:, 3].astype(np.int64)
        t_min_abs   = timestamps[0]
        total_end_sec = t_min_abs + int((start_min + n_spectra * t_per_min) * 60)
        t_start_abs = t_min_abs + int(start_min * 60)

        # Use a fast integer-shift approximation for the map
        x_px = raw_points[:, 0].astype(int)
        y_px = raw_points[:, 1].astype(int)
        ts   = raw_points[:, 3].astype(np.int64)

        valid = (x_px >= 0) & (x_px < 8192) & (y_px >= 0) & (y_px < 8192) & \
                (y_px >= y_start) & (y_px <= y_end) & \
                (ts >= t_start_abs) & (ts <= total_end_sec)
        x_px, y_px, ts = x_px[valid], y_px[valid], ts[valid]

        # Integer curvature correction per event
        shift_per_event = np.round(-detector_shift[y_px]).astype(int)
        x_corrected = np.clip(x_px + shift_per_event, 0, len(emission_energy) - 1)

        # Convert timestamp to minutes from start of acquisition
        time_minutes = (ts - timestamps[0]) / 60.0

        n_channels = len(emission_energy)
        # 2D histogram: rows = time, cols = emission energy
        rixs_map, t_edges, e_edges = np.histogram2d(
            time_minutes, x_corrected,
            bins=[n_map_bins, n_channels],
            range=[[start_min, start_min + n_spectra * t_per_min],
                   [0, n_channels]])

        # Map channel indices to emission energy values
        e_centers = (e_edges[:-1] + e_edges[1:]) / 2.0
        e_axis    = np.interp(e_centers, np.arange(n_channels), emission_energy)
        t_centers = (t_edges[:-1] + t_edges[1:]) / 2.0

        return rixs_map, t_edges, e_axis, t_edges

    # ------------------------------------------------------------------
    def _x_axis_values(self, emission_energy_array):
        p = self.parameters
        if p.get("veritas_time_rixs_plot_energy_type") == "Energy loss":
            ie = float(p["veritas_time_rixs_incoming_energy"])
            return emission_energy_array - ie  # negative = inelastic loss
        return emission_energy_array

    # ------------------------------------------------------------------
    def _load_and_plot(self):
        plt.close('all')
        self._load_raw_data()
        print("Computing extracted spectra …")
        self._compute_extracted_spectra()
        print("Building RIXS color map …")
        rixs_map, t_edges, e_axis_map, _ = self._build_rixs_map()

        p = self.parameters
        n_spectra = int(p["veritas_time_rixs_number_of_spectra"])
        start_min = float(p.get("veritas_time_rixs_start_time_minutes", "0"))
        t_per_min = float(p["veritas_time_rixs_time_per_spectra_minutes"])
        colormap  = p.get("plot_colormap_choice", "turbo")

        colors = list(cm.rainbow(np.linspace(0, 1, n_spectra)))

        # Apply x-axis conversion to map energy axis
        if p.get("veritas_time_rixs_plot_energy_type") == "Energy loss":
            ie = float(p["veritas_time_rixs_incoming_energy"])
            x_axis_map = e_axis_map - ie
        else:
            x_axis_map = e_axis_map

        # ---- Figure 1: RIXS color map ----
        fig_map, ax_map = plt.subplots(figsize=(10, 7))
        t_edges_plot = t_edges
        pcm = ax_map.pcolormesh(
            np.concatenate([[x_axis_map[0] - (x_axis_map[1] - x_axis_map[0]) / 2],
                             (x_axis_map[:-1] + x_axis_map[1:]) / 2,
                             [x_axis_map[-1] + (x_axis_map[-1] - x_axis_map[-2]) / 2]]),
            t_edges_plot,
            rixs_map,
            cmap=colormap,
            shading='flat')
        fig_map.colorbar(pcm, ax=ax_map, label='Counts')

        # Overlay colored horizontal bands for each spectrum
        for seg in range(n_spectra):
            t0 = start_min + seg * t_per_min
            t1 = t0 + t_per_min
            ax_map.axhspan(t0, t1, alpha=0.18, color=colors[seg],
                           label="Spectrum {}  ({:.1f}–{:.1f} min)".format(seg + 1, t0, t1))
            ax_map.axhline(t0, color=colors[seg], linewidth=1.2, linestyle='--')
        ax_map.axhline(start_min + n_spectra * t_per_min,
                       color=colors[-1], linewidth=1.2, linestyle='--')

        x_label = "Energy loss [eV]" if p.get("veritas_time_rixs_plot_energy_type") == "Energy loss" \
                  else "Emission energy [eV]"
        ax_map.set_xlabel(x_label, fontsize=14)
        ax_map.set_ylabel("Time [minutes]", fontsize=14)
        ax_map.set_title("RIXS time-resolved map  —  acq {}".format(
            p["veritas_time_rixs_acquisition_number"]), fontsize=14)
        ax_map.legend(fontsize=9, loc="upper right")
        fig_map.tight_layout()
        fig_map.show()

        # ---- Figure 2: extracted line scans ----
        fig_lines, ax_lines = plt.subplots(figsize=(10, 6))
        for seg in range(n_spectra):
            x_vals = self._x_axis_values(self._last_array_of_x_value_arrays[seg])
            y_vals = self._last_array_of_intensity_arrays[seg]
            t0 = start_min + seg * t_per_min
            t1 = t0 + t_per_min
            ax_lines.plot(x_vals, y_vals, color=colors[seg],
                          label="Spectrum {}  ({:.1f}–{:.1f} min)".format(seg + 1, t0, t1))

        ax_lines.set_xlabel(x_label, fontsize=14)
        ax_lines.set_ylabel("Intensity [counts]", fontsize=14)
        ax_lines.set_title("Extracted RIXS spectra", fontsize=14)
        ax_lines.legend(fontsize=9)
        fig_lines.tight_layout()
        fig_lines.show()

        print("Plots updated.")

    # ------------------------------------------------------------------
    def closeEvent(self, event):
        if event.spontaneous():
            self.parameters["is_program_running"] = False
            self.finished.emit()
        event.accept()

    def save_and_continue(self):
        parameter_scripts.save_parameters(self.parameters)
        self._save_treated_data()
        plt.close('all')
        self.finished.emit()
        self.close()

    def save_and_close(self):
        parameter_scripts.save_parameters(self.parameters)
        self._save_treated_data()
        self.parameters["is_program_running"] = False
        plt.close('all')
        self.finished.emit()
        self.close()

    def close_program(self):
        self.parameters["is_program_running"] = False
        plt.close('all')
        self.finished.emit()
        self.close()

    def get_inputted_parameters_from_gui(self):
        return self.parameters

    # ------------------------------------------------------------------
    def _save_treated_data(self):
        if self._last_array_of_intensity_arrays is None:
            print("Nothing to save — run Update the plot first.")
            return

        p = self.parameters
        ie = float(p["veritas_time_rixs_incoming_energy"])
        n_spectra = len(self._last_array_of_intensity_arrays)
        start_min = float(p.get("veritas_time_rixs_start_time_minutes", "0"))
        t_per_min = float(p["veritas_time_rixs_time_per_spectra_minutes"])

        energy_type = p.get("veritas_time_rixs_plot_energy_type", "Emission energy")

        figure_name = "RIXS_time_resolved"
        figure_name += "_" + p["output_file_element"]
        figure_name += "_" + p["output_file_edge"]
        figure_name += "_" + p["output_file_sample_name"]
        figure_name += "_acq" + p["veritas_time_rixs_acquisition_number"]
        figure_name += "_{}spectra_{}minEach".format(n_spectra, int(t_per_min))
        if p["output_file_additional_comment"]:
            figure_name += "_" + p["output_file_additional_comment"]

        figure_path = os.path.join(p["input_file_project_folder"], "Simple RIXS Figures")
        os.makedirs(figure_path, exist_ok=True)

        data_dict = {}
        for seg in range(n_spectra):
            x_vals = self._x_axis_values(self._last_array_of_x_value_arrays[seg])
            y_vals = self._last_array_of_intensity_arrays[seg]
            t_center = self._last_time_centers_minutes[seg]
            col_prefix = "{} [eV]_spectra_{}_{}".format(
                "Energy loss" if energy_type == "Energy loss" else "Emission energy",
                seg, round(t_center, 2))
            data_dict[col_prefix] = x_vals
            data_dict["Intensity [counts]_spectra_{}_{}".format(seg, round(t_center, 2))] = y_vals

        df = pd.DataFrame.from_dict(data_dict, orient='index').transpose().fillna('')
        data_path = os.path.join(figure_path, figure_name + "_data.txt")
        df.to_csv(data_path, sep='\t', index=False)

        params_path = os.path.join(figure_path, figure_name + "_parameters.txt")
        with open(params_path, "w") as f:
            f.write(json.dumps(self.parameters, indent=0))

        print("Saved to:", data_path)
