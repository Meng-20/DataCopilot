"""
Plotting utilities for Research Data Copilot.

Generated plots are saved to:

    DataCopilot/out/
"""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import matplotlib

# Use a non-GUI backend on the remote Linux server.
# This must appear before importing matplotlib.pyplot.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


# ============================================================
# Output configuration
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

OUTPUT_DIR = PROJECT_ROOT / "out"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Shared helper functions
# ============================================================

def create_output_path(
    prefix: str
) -> Path:
    """
    Create a unique PNG output path.
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    unique_id = uuid4().hex[:8]

    return (
        OUTPUT_DIR
        / (
            f"{prefix}_"
            f"{timestamp}_"
            f"{unique_id}.png"
        )
    )


def save_figure(
    figure,
    prefix: str
) -> str:
    """
    Save and close a Matplotlib figure.

    Returns:
        Absolute filename as a string.
    """

    filename = create_output_path(
        prefix
    )

    figure.tight_layout()

    figure.savefig(
        filename,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close(figure)

    return str(filename)


def validate_columns(
    df: pd.DataFrame,
    required_columns: list[str]
) -> None:
    """
    Check whether required columns exist.
    """

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )


def prepare_xy_data(
    df: pd.DataFrame,
    x: str,
    y: str,
    sort_by_x: bool = False
) -> pd.DataFrame:
    """
    Prepare two numeric columns for plotting.
    """

    validate_columns(
        df,
        [x, y]
    )

    plot_df = df[[x, y]].copy()

    plot_df[x] = pd.to_numeric(
        plot_df[x],
        errors="coerce"
    )

    plot_df[y] = pd.to_numeric(
        plot_df[y],
        errors="coerce"
    )

    plot_df = plot_df.dropna()

    if plot_df.empty:
        raise ValueError(
            f"No valid numeric data "
            f"for '{x}' and '{y}'"
        )

    if sort_by_x:
        plot_df = plot_df.sort_values(
            by=x
        )

    return plot_df


def get_valid_savgol_window(
    requested_window: int,
    data_length: int,
    polynomial_order: int
) -> int:
    """
    Return a valid Savitzky-Golay window.

    The window must:
        - be odd;
        - exceed polynomial_order;
        - not exceed the data length.
    """

    if requested_window < 3:
        raise ValueError(
            "smoothing_window must be at least 3"
        )

    if polynomial_order < 1:
        raise ValueError(
            "polynomial_order must be at least 1"
        )

    if data_length <= polynomial_order:
        raise ValueError(
            "Not enough data points for smoothing"
        )

    window = min(
        requested_window,
        data_length
    )

    if window % 2 == 0:
        window -= 1

    minimum_window = polynomial_order + 2

    if minimum_window % 2 == 0:
        minimum_window += 1

    window = max(
        window,
        minimum_window
    )

    if window > data_length:
        window = (
            data_length
            if data_length % 2 == 1
            else data_length - 1
        )

    if window <= polynomial_order:
        raise ValueError(
            "Savitzky-Golay window must be "
            "greater than polynomial order"
        )

    return window


# ============================================================
# Generic plots
# ============================================================

def scatter_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str | None = None
) -> str:
    """
    Create a scatter plot.
    """

    plot_df = prepare_xy_data(
        df=df,
        x=x,
        y=y,
        sort_by_x=False
    )

    figure, axis = plt.subplots(
        figsize=(10, 6)
    )

    axis.scatter(
        plot_df[x],
        plot_df[y],
        alpha=0.5,
        s=12
    )

    axis.set_xlabel(x)
    axis.set_ylabel(y)

    axis.set_title(
        title or f"{y} vs {x}"
    )

    axis.grid(
        alpha=0.3
    )

    return save_figure(
        figure,
        "scatter_plot"
    )


def line_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str | None = None
) -> str:
    """
    Create a line plot.
    """

    plot_df = prepare_xy_data(
        df=df,
        x=x,
        y=y,
        sort_by_x=True
    )

    figure, axis = plt.subplots(
        figsize=(12, 6)
    )

    axis.plot(
        plot_df[x],
        plot_df[y],
        linewidth=1
    )

    axis.set_xlabel(x)
    axis.set_ylabel(y)

    axis.set_title(
        title or f"{y} vs {x}"
    )

    axis.grid(
        alpha=0.3
    )

    return save_figure(
        figure,
        "cycle_plot"
    )


# ============================================================
# Capacity-retention plot
# ============================================================

def capacity_retention_plot(
    cycle_df: pd.DataFrame
) -> str:
    """
    Plot discharge-capacity retention versus cycle.

    The first valid positive discharge capacity is used
    as the 100% baseline.
    """

    cycle_column = "Cycle_Index"

    capacity_column = (
        "Discharge_Capacity(Ah)"
    )

    validate_columns(
        cycle_df,
        [
            cycle_column,
            capacity_column
        ]
    )

    plot_df = cycle_df[
        [
            cycle_column,
            capacity_column
        ]
    ].copy()

    plot_df[cycle_column] = pd.to_numeric(
        plot_df[cycle_column],
        errors="coerce"
    )

    plot_df[capacity_column] = pd.to_numeric(
        plot_df[capacity_column],
        errors="coerce"
    )

    plot_df = (
        plot_df
        .dropna()
        .sort_values(
            by=cycle_column
        )
    )

    plot_df = plot_df[
        plot_df[capacity_column] > 0
    ]

    if plot_df.empty:
        raise ValueError(
            "No valid positive discharge "
            "capacity data found"
        )

    initial_capacity = float(
        plot_df[
            capacity_column
        ].iloc[0]
    )

    retention = (
        plot_df[capacity_column]
        / initial_capacity
        * 100.0
    )

    figure, axis = plt.subplots(
        figsize=(10, 6)
    )

    axis.plot(
        plot_df[cycle_column],
        retention,
        marker="o",
        markersize=4,
        linewidth=1.8,
        label="Capacity retention"
    )

    axis.axhline(
        y=80,
        color="red",
        linestyle="--",
        linewidth=1.2,
        label="80% reference"
    )

    axis.set_xlabel(
        "Cycle Index"
    )

    axis.set_ylabel(
        "Capacity Retention (%)"
    )

    axis.set_title(
        "Capacity Retention Curve"
    )

    axis.grid(
        alpha=0.3
    )

    axis.legend()

    return save_figure(
        figure,
        "capacity_retention"
    )


# ============================================================
# Capacity-voltage plot
# ============================================================

def capacity_voltage_plot(
    cycle_df: pd.DataFrame,
    cycle: int,
    mode: str = "both"
) -> str:
    """
    Plot capacity versus voltage for one cycle.

    Supported modes:
        charge
        discharge
        both

    Current convention:
        Current > 0 means charge.
        Current < 0 means discharge.
    """

    valid_modes = {
        "charge",
        "discharge",
        "both"
    }

    if mode not in valid_modes:
        raise ValueError(
            "mode must be charge, "
            "discharge, or both"
        )

    current_column = "Current(A)"
    voltage_column = "Voltage(V)"

    charge_capacity_column = (
        "Charge_Capacity(Ah)"
    )

    discharge_capacity_column = (
        "Discharge_Capacity(Ah)"
    )

    validate_columns(
        cycle_df,
        [
            current_column,
            voltage_column,
            charge_capacity_column,
            discharge_capacity_column
        ]
    )

    figure, axis = plt.subplots(
        figsize=(10, 6)
    )

    plotted = False

    if mode in {
        "charge",
        "both"
    }:
        charge_df = cycle_df.loc[
            cycle_df[current_column] > 0,
            [
                charge_capacity_column,
                voltage_column
            ]
        ].copy()

        charge_df = (
            charge_df
            .dropna()
            .sort_values(
                by=charge_capacity_column
            )
        )

        if not charge_df.empty:
            axis.plot(
                charge_df[
                    charge_capacity_column
                ],
                charge_df[
                    voltage_column
                ],
                linewidth=2,
                label="Charge"
            )

            plotted = True

    if mode in {
        "discharge",
        "both"
    }:
        discharge_df = cycle_df.loc[
            cycle_df[current_column] < 0,
            [
                discharge_capacity_column,
                voltage_column
            ]
        ].copy()

        discharge_df = (
            discharge_df
            .dropna()
            .sort_values(
                by=discharge_capacity_column
            )
        )

        if not discharge_df.empty:
            axis.plot(
                discharge_df[
                    discharge_capacity_column
                ],
                discharge_df[
                    voltage_column
                ],
                linewidth=2,
                label="Discharge"
            )

            plotted = True

    if not plotted:
        plt.close(figure)

        raise ValueError(
            f"No valid {mode} data "
            f"found for cycle {cycle}"
        )

    axis.set_xlabel(
        "Capacity (Ah)"
    )

    axis.set_ylabel(
        "Voltage (V)"
    )

    axis.set_title(
        f"Cycle {cycle}: "
        "Capacity-Voltage Curve"
    )

    axis.grid(
        alpha=0.3
    )

    axis.legend()

    return save_figure(
        figure,
        (
            f"capacity_voltage_"
            f"cycle_{cycle}_{mode}"
        )
    )


# ============================================================
# dQ/dV calculation
# ============================================================

def calculate_dqdv(
    cycle_df: pd.DataFrame,
    mode: str = "discharge",
    voltage_bin_width: float = 0.005,
    smoothing_window: int = 11,
    polynomial_order: int = 2
) -> dict:
    """
    Calculate dQ/dV data for one cycle.

    Processing:
        1. Select charge or discharge data.
        2. Remove missing and low-current records.
        3. Group samples into voltage bins.
        4. Smooth capacity.
        5. Calculate dQ/dV.

    For discharge, this returns -dQ/dV so that the
    primary discharge curve is normally displayed upward.

    This function currently includes all positive-current
    records for charge and all negative-current records
    for discharge. It does not select a specific Step_Index.
    """

    if mode == "charge":
        capacity_column = (
            "Charge_Capacity(Ah)"
        )

    elif mode == "discharge":
        capacity_column = (
            "Discharge_Capacity(Ah)"
        )

    else:
        raise ValueError(
            "mode must be charge or discharge"
        )

    validate_columns(
        cycle_df,
        [
            "Voltage(V)",
            "Current(A)",
            capacity_column
        ]
    )

    if voltage_bin_width <= 0:
        raise ValueError(
            "voltage_bin_width must "
            "be greater than zero"
        )

    if mode == "charge":
        mode_mask = (
            pd.to_numeric(
                cycle_df["Current(A)"],
                errors="coerce"
            )
            > 0
        )

    else:
        mode_mask = (
            pd.to_numeric(
                cycle_df["Current(A)"],
                errors="coerce"
            )
            < 0
        )

    analysis_df = cycle_df.loc[
        mode_mask,
        [
            "Voltage(V)",
            "Current(A)",
            capacity_column
        ]
    ].copy()

    numeric_columns = [
        "Voltage(V)",
        "Current(A)",
        capacity_column
    ]

    for column in numeric_columns:
        analysis_df[column] = pd.to_numeric(
            analysis_df[column],
            errors="coerce"
        )

    analysis_df = analysis_df.dropna()

    if len(analysis_df) < 10:
        raise ValueError(
            f"Not enough {mode} records "
            "to calculate dQ/dV"
        )

    maximum_current = float(
        analysis_df[
            "Current(A)"
        ]
        .abs()
        .max()
    )

    if (
        not np.isfinite(maximum_current)
        or maximum_current <= 0
    ):
        raise ValueError(
            f"No valid {mode} current data"
        )

    current_threshold = (
        maximum_current * 0.05
    )

    analysis_df = analysis_df[
        analysis_df[
            "Current(A)"
        ]
        .abs()
        >= current_threshold
    ].copy()

    if len(analysis_df) < 10:
        raise ValueError(
            "Not enough records remain "
            "after current filtering"
        )

    analysis_df["voltage_bin"] = (
        analysis_df["Voltage(V)"]
        / voltage_bin_width
    ).round() * voltage_bin_width

    binned_df = (
        analysis_df
        .groupby(
            "voltage_bin",
            as_index=False
        )[capacity_column]
        .mean()
        .sort_values(
            by="voltage_bin"
        )
    )

    voltage = (
        binned_df[
            "voltage_bin"
        ]
        .to_numpy(
            dtype=float
        )
    )

    capacity = (
        binned_df[
            capacity_column
        ]
        .to_numpy(
            dtype=float
        )
    )

    finite_mask = (
        np.isfinite(voltage)
        &
        np.isfinite(capacity)
    )

    voltage = voltage[
        finite_mask
    ]

    capacity = capacity[
        finite_mask
    ]

    if len(voltage) < 5:
        raise ValueError(
            "Not enough voltage bins "
            "to calculate dQ/dV"
        )

    voltage, unique_indices = np.unique(
        voltage,
        return_index=True
    )

    capacity = capacity[
        unique_indices
    ]

    if len(voltage) < 5:
        raise ValueError(
            "Not enough unique voltage "
            "values to calculate dQ/dV"
        )

    actual_window = get_valid_savgol_window(
        requested_window=(
            smoothing_window
        ),
        data_length=len(capacity),
        polynomial_order=(
            polynomial_order
        )
    )

    smoothed_capacity = savgol_filter(
        capacity,
        window_length=actual_window,
        polyorder=polynomial_order
    )

    dqdv = np.gradient(
        smoothed_capacity,
        voltage
    )

    if mode == "discharge":
        dqdv = -dqdv

    valid_mask = (
        np.isfinite(voltage)
        &
        np.isfinite(dqdv)
    )

    voltage = voltage[
        valid_mask
    ]

    dqdv = dqdv[
        valid_mask
    ]

    if len(voltage) == 0:
        raise ValueError(
            "No valid dQ/dV values "
            "could be calculated"
        )

    return {
        "voltage": voltage,

        "dqdv": dqdv,

        "point_count": int(
            len(voltage)
        ),

        "voltage_min": float(
            voltage.min()
        ),

        "voltage_max": float(
            voltage.max()
        ),

        "dqdv_min": float(
            dqdv.min()
        ),

        "dqdv_max": float(
            dqdv.max()
        ),

        "voltage_bin_width": float(
            voltage_bin_width
        ),

        "smoothing_window": int(
            actual_window
        ),

        "polynomial_order": int(
            polynomial_order
        )
    }


# ============================================================
# Single-cycle dQ/dV plot
# ============================================================

def dqdv_plot(
    cycle_df: pd.DataFrame,
    cycle: int,
    mode: str = "discharge",
    voltage_bin_width: float = 0.005,
    smoothing_window: int = 11,
    polynomial_order: int = 2
) -> str:
    """
    Plot a single-cycle dQ/dV curve.
    """

    result = calculate_dqdv(
        cycle_df=cycle_df,
        mode=mode,
        voltage_bin_width=(
            voltage_bin_width
        ),
        smoothing_window=(
            smoothing_window
        ),
        polynomial_order=(
            polynomial_order
        )
    )

    figure, axis = plt.subplots(
        figsize=(10, 6)
    )

    axis.plot(
        result["voltage"],
        result["dqdv"],
        linewidth=1.8,
        label=(
            f"Cycle {cycle} "
            f"{mode.capitalize()}"
        )
    )

    axis.set_xlabel(
        "Voltage (V)"
    )

    axis.set_ylabel(
        "-dQ/dV (Ah/V)"
        if mode == "discharge"
        else "dQ/dV (Ah/V)"
    )

    axis.set_title(
        f"Cycle {cycle}: "
        f"{mode.capitalize()} "
        "Incremental Capacity"
    )

    axis.grid(
        alpha=0.3
    )

    axis.legend()

    return save_figure(
        figure,
        (
            f"dqdv_cycle_"
            f"{cycle}_{mode}"
        )
    )


# ============================================================
# Two-cycle dQ/dV comparison plot
# ============================================================

def cycle_comparison_dqdv_plot(
    raw_df: pd.DataFrame,
    cycle1: int,
    cycle2: int,
    mode: str = "discharge",
    voltage_bin_width: float = 0.005,
    smoothing_window: int = 11,
    polynomial_order: int = 2,
    common_voltage_range: bool = True
) -> dict:
    """
    Compare dQ/dV curves for two cycles.

    When common_voltage_range is True, only the voltage
    interval shared by both cycles is displayed.

    Returns a dictionary because cycle.py expects:

        result["filename"]
    """

    validate_columns(
        raw_df,
        ["Cycle_Index"]
    )

    if cycle1 == cycle2:
        raise ValueError(
            "cycle1 and cycle2 must be different"
        )

    cycle1_df = raw_df[
        raw_df["Cycle_Index"] == cycle1
    ].copy()

    cycle2_df = raw_df[
        raw_df["Cycle_Index"] == cycle2
    ].copy()

    if cycle1_df.empty:
        raise ValueError(
            f"Cycle {cycle1} not found"
        )

    if cycle2_df.empty:
        raise ValueError(
            f"Cycle {cycle2} not found"
        )

    cycle1_result = calculate_dqdv(
        cycle_df=cycle1_df,
        mode=mode,
        voltage_bin_width=(
            voltage_bin_width
        ),
        smoothing_window=(
            smoothing_window
        ),
        polynomial_order=(
            polynomial_order
        )
    )

    cycle2_result = calculate_dqdv(
        cycle_df=cycle2_df,
        mode=mode,
        voltage_bin_width=(
            voltage_bin_width
        ),
        smoothing_window=(
            smoothing_window
        ),
        polynomial_order=(
            polynomial_order
        )
    )

    cycle1_voltage = (
        cycle1_result["voltage"]
    )

    cycle1_dqdv = (
        cycle1_result["dqdv"]
    )

    cycle2_voltage = (
        cycle2_result["voltage"]
    )

    cycle2_dqdv = (
        cycle2_result["dqdv"]
    )

    common_voltage_min = max(
        cycle1_result["voltage_min"],
        cycle2_result["voltage_min"]
    )

    common_voltage_max = min(
        cycle1_result["voltage_max"],
        cycle2_result["voltage_max"]
    )

    if common_voltage_range:
        if (
            common_voltage_min
            >= common_voltage_max
        ):
            raise ValueError(
                "The selected cycles have "
                "no overlapping voltage range"
            )

        cycle1_mask = (
            (
                cycle1_voltage
                >= common_voltage_min
            )
            &
            (
                cycle1_voltage
                <= common_voltage_max
            )
        )

        cycle2_mask = (
            (
                cycle2_voltage
                >= common_voltage_min
            )
            &
            (
                cycle2_voltage
                <= common_voltage_max
            )
        )

        cycle1_voltage = cycle1_voltage[
            cycle1_mask
        ]

        cycle1_dqdv = cycle1_dqdv[
            cycle1_mask
        ]

        cycle2_voltage = cycle2_voltage[
            cycle2_mask
        ]

        cycle2_dqdv = cycle2_dqdv[
            cycle2_mask
        ]

        if (
            len(cycle1_voltage) == 0
            or len(cycle2_voltage) == 0
        ):
            raise ValueError(
                "No dQ/dV points remain "
                "in the common voltage range"
            )

    figure, axis = plt.subplots(
        figsize=(11, 6)
    )

    axis.plot(
        cycle1_voltage,
        cycle1_dqdv,
        linewidth=2,
        label=f"Cycle {cycle1}"
    )

    axis.plot(
        cycle2_voltage,
        cycle2_dqdv,
        linewidth=2,
        label=f"Cycle {cycle2}"
    )

    axis.set_xlabel(
        "Voltage (V)"
    )

    axis.set_ylabel(
        "-dQ/dV (Ah/V)"
        if mode == "discharge"
        else "dQ/dV (Ah/V)"
    )

    axis.set_title(
        f"{mode.capitalize()} "
        "Incremental Capacity Comparison: "
        f"Cycle {cycle1} vs Cycle {cycle2}"
    )

    axis.grid(
        alpha=0.3
    )

    axis.legend()

    filename = save_figure(
        figure,
        (
            f"dqdv_comparison_"
            f"cycle_{cycle1}_"
            f"cycle_{cycle2}_"
            f"{mode}"
        )
    )

    return {
        "filename": filename,

        "mode": mode,

        "cycle1": cycle1,

        "cycle2": cycle2,

        "cycle1_points": int(
            len(cycle1_voltage)
        ),

        "cycle2_points": int(
            len(cycle2_voltage)
        ),

        "common_voltage_range":
            common_voltage_range,

        "common_voltage_min": (
            float(common_voltage_min)
            if common_voltage_range
            else None
        ),

        "common_voltage_max": (
            float(common_voltage_max)
            if common_voltage_range
            else None
        )
    }