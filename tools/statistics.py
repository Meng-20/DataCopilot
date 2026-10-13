import pandas as pd

def average(df, column):
    return {
        "column": column,
        "average": float(df[column].mean())
    }