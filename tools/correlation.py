def correlation(df, x, y):

    if x not in df.columns:
        return {
            "error": f"{x} not found"
        }

    if y not in df.columns:
        return {
            "error": f"{y} not found"
        }

    corr = df[x].corr(df[y])

    return {
        "x": x,
        "y": y,
        "correlation": float(corr)
    }
    
def target_correlations(
        df,
        target):

    numeric_df = df.select_dtypes(
        include="number"
    )

    corr = numeric_df.corr()[target]

    corr = corr.sort_values(
        ascending=False
    )

    return corr.to_dict()

def top_correlations(
        df,
        target):

    numeric_df = df.select_dtypes(
        include="number"
    )

    corr = (
        numeric_df
        .corr()[target]
        .sort_values(
            key=abs,
            ascending=False
        )
    )

    return corr.to_dict()