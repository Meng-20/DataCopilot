from fastapi import APIRouter
from fastapi.responses import FileResponse

from core.datastore import datasets

from tools.plotting import (
    line_plot,
    capacity_retention_plot,
    capacity_voltage_plot,
    dqdv_plot,
    cycle_comparison_dqdv_plot
)

router = APIRouter()

@router.get("/cycle-list")
def cycle_list():

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    cycles = sorted(
        datasets["raw_data"]
        ["Cycle_Index"]
        .dropna()
        .unique()
        .tolist()
    )

    return {
        "cycles": cycles,
        "count": len(cycles)
    }
    
@router.get("/cycle-summary")
def cycle_summary(
    cycle: int
):

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    df = datasets["raw_data"]

    cycle_df = df[
        df["Cycle_Index"] == cycle
    ]

    if cycle_df.empty:
        return {
            "error": f"cycle {cycle} not found"
        }

    return {
        "cycle": cycle,

        "records": len(cycle_df),

        "max_voltage":
            float(
                cycle_df["Voltage(V)"].max()
            ),

        "min_voltage":
            float(
                cycle_df["Voltage(V)"].min()
            ),

        "charge_capacity":
            float(
                cycle_df[
                    "Charge_Capacity(Ah)"
                ].max()
            ),

        "discharge_capacity":
            float(
                cycle_df[
                    "Discharge_Capacity(Ah)"
                ].max()
            ),

        "charge_energy":
            float(
                cycle_df[
                    "Charge_Energy(Wh)"
                ].max()
            ),

        "discharge_energy":
            float(
                cycle_df[
                    "Discharge_Energy(Wh)"
                ].max()
            )
    }
    
@router.get("/cycle-steps")
def cycle_steps(
    cycle: int
):

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    df = datasets["raw_data"]

    cycle_df = df[
        df["Cycle_Index"] == cycle
    ]

    if cycle_df.empty:
        return {
            "error": f"cycle {cycle} not found"
        }

    step_summary = (
        cycle_df
        .groupby("Step_Index")
        .agg(
            records=("Voltage(V)", "size"),

            current_mean=("Current(A)", "mean"),
            current_min=("Current(A)", "min"),
            current_max=("Current(A)", "max"),

            voltage_min=("Voltage(V)", "min"),
            voltage_max=("Voltage(V)", "max"),

            duration_seconds=(
                "Step_Time(s)",
                "max"
            )
        )
        .reset_index()
    )

    step_summary["voltage_span"] = (
        step_summary["voltage_max"]
        -
        step_summary["voltage_min"]
    )

    return {
        "cycle": cycle,
        "steps":
            step_summary
            .round(6)
            .to_dict("records")
    }
    
@router.get("/cycle-plot")
def cycle_plot(
    cycle: int,
    x: str,
    y: str
):

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    df = datasets["raw_data"]

    cycle_df = df[
        df["Cycle_Index"] == cycle
    ]

    if cycle_df.empty:
        return {
            "error": f"cycle {cycle} not found"
        }

    image = line_plot(
        cycle_df,
        x,
        y,
        title=f"Cycle {cycle}: {y} vs {x}"
    )

    return FileResponse(image)

@router.get("/cycle-comparison")
def compare_cycles(
    cycle1: int,
    cycle2: int
):

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    df = datasets["raw_data"]

    c1 = df[
        df["Cycle_Index"] == cycle1
    ]

    c2 = df[
        df["Cycle_Index"] == cycle2
    ]

    if c1.empty or c2.empty:
        return {
            "error": "cycle not found"
        }

    cap1 = float(
        c1[
            "Discharge_Capacity(Ah)"
        ].max()
    )

    cap2 = float(
        c2[
            "Discharge_Capacity(Ah)"
        ].max()
    )

    fade = (
        (cap1 - cap2)
        /
        cap1
        * 100
    )

    return {
        "cycle1": {
            "cycle": cycle1,
            "capacity": round(cap1, 6)
        },

        "cycle2": {
            "cycle": cycle2,
            "capacity": round(cap2, 6)
        },

        "capacity_fade_percent":
            round(fade, 2)
    }

@router.get("/capacity-retention")
def capacity_retention():

    if "cycle_stats" not in datasets:
        return {
            "error": "upload dataset first"
        }

    df = datasets["cycle_stats"]

    initial_capacity = (
        df[
            "Discharge_Capacity(Ah)"
        ].iloc[0]
    )

    latest_capacity = (
        df[
            "Discharge_Capacity(Ah)"
        ].iloc[-1]
    )

    retention = (
        latest_capacity
        /
        initial_capacity
        * 100
    )

    return {
        "retention_percent":
            round(
                float(retention),
                2
            )
    }
    
@router.get("/capacity-retention-curve")
def capacity_retention_curve():

    if "cycle_stats" not in datasets:
        return {
            "error": "upload dataset first"
        }

    image = capacity_retention_plot(
        datasets["cycle_stats"]
    )

    return FileResponse(image)

@router.get("/capacity-voltage-curve")
def capacity_voltage_curve(
    cycle: int,
    mode: str = "both"
):

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    cycle_df = datasets[
        "raw_data"
    ][
        datasets["raw_data"]
        ["Cycle_Index"]
        == cycle
    ]

    image = capacity_voltage_plot(
        cycle_df,
        cycle,
        mode
    )

    return FileResponse(image)

@router.get("/dqdv-curve")
def dqdv_curve(
    cycle: int,
    mode: str = "discharge",
    voltage_bin_width: float = 0.005,
    smoothing_window: int = 11
):

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    cycle_df = datasets[
        "raw_data"
    ][
        datasets["raw_data"]
        ["Cycle_Index"]
        == cycle
    ]

    image = dqdv_plot(
        cycle_df=cycle_df,
        cycle=cycle,
        mode=mode,
        voltage_bin_width=(
            voltage_bin_width
        ),
        smoothing_window=(
            smoothing_window
        )
    )

    return FileResponse(image)

@router.get("/cycle-comparison-dqdv")
def cycle_comparison_dqdv(
    cycle1: int,
    cycle2: int,
    mode: str = "discharge",
    voltage_bin_width: float = 0.005,
    smoothing_window: int = 11
):

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    result = (
        cycle_comparison_dqdv_plot(
            raw_df=datasets[
                "raw_data"
            ],

            cycle1=cycle1,

            cycle2=cycle2,

            mode=mode,

            voltage_bin_width=(
                voltage_bin_width
            ),

            smoothing_window=(
                smoothing_window
            )
        )
    )

    return FileResponse(result)
