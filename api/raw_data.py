from fastapi import APIRouter
from fastapi.responses import FileResponse

from core.datastore import datasets

from tools.correlation import correlation
from tools.correlation import top_correlations

from tools.plotting import scatter_plot

router = APIRouter()


@router.get("/raw-columns")
def raw_columns():

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    return {
        "columns":
            datasets[
                "raw_data"
            ].columns.tolist()
    }


@router.get("/correlation")
def get_correlation(
    x: str,
    y: str
):

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    return correlation(
        datasets["raw_data"],
        x,
        y
    )


@router.get("/top-correlations")
def get_top_correlations(
    target: str
):

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    return top_correlations(
        datasets["raw_data"],
        target
    )


@router.get("/plot")
def plot(
    x: str,
    y: str
):

    if "raw_data" not in datasets:
        return {
            "error": "upload dataset first"
        }

    image = scatter_plot(
        datasets["raw_data"],
        x,
        y
    )

    return FileResponse(image)