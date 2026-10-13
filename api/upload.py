from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

import pandas as pd

from core.datastore import datasets

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):

    excel = pd.ExcelFile(file.file)

    datasets.clear()

    # Global Info
    datasets["global_info"] = pd.read_excel(
        excel,
        sheet_name="Global_Info"
    )

    # Raw Data
    raw_1 = pd.read_excel(
        excel,
        sheet_name="Channel_1-008_1"
    )

    raw_2 = pd.read_excel(
        excel,
        sheet_name="Channel_1-008_2"
    )

    datasets["raw_data"] = pd.concat(
        [raw_1, raw_2],
        ignore_index=True
    )

    # Cycle Summary
    datasets["cycle_stats"] = pd.read_excel(
        excel,
        sheet_name="StatisticsByCycle_1-008"
    )

    return {
        "datasets":
            list(datasets.keys()),

        "raw_rows":
            len(datasets["raw_data"]),

        "cycle_rows":
            len(datasets["cycle_stats"])
    }