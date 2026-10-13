from fastapi import APIRouter
from core.datastore import datasets

router = APIRouter()

@router.get("/")
def root():

    return {
        "message":
            "Research Data Copilot"
    }

@router.get("/datasets")
def get_datasets():

    return {
        "datasets":
            list(datasets.keys())
    }