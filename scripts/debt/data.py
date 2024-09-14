import pandas as pd
from bblocks import set_bblocks_data_path, DebtIDS, convert_id

from scripts import config
from scripts.dac_data.tools import key_statistics
from scripts.drm.tools import (
    to_constant,
)
from scripts.tools import export_json

set_bblocks_data_path(config.Paths.raw_data)

NON_MDBs = [
    "Arab Monetary Fund",
    "Arab Fund for Economic & Social Development",
    "OPEC Fund for International Dev.",
    "Plata Basin Financial Dev. Fund",
    "International Finance Corporation",
    "African Export-Import Bank",
    "European Social Fund (ESF)",
    "European Development Fund (EDF)",
    "Nordic Investment Bank",
    "Arab African International Bank",
]


def exclude_non_mdbs(df: pd.DataFrame):
    return df.loc[lambda d: ~d.counterpart_area.isin(NON_MDBs)]


def get_non_concessional_lending(
    indicator: str = "bilateral",
    start_year: int = 2017,
    end_year: int = 2023,
    exclude_china_counterpart: bool = True,
    exclude_china_country: bool = True,
    only_mdbs: bool = True,
    prices: str = "constant",
) -> pd.DataFrame:

    if indicator == "bilateral":
        indicator1, indicator2 = "DT.DIS.BLAT.CD", "DT.DIS.BLTC.CD"
    else:
        indicator1, indicator2 = "DT.DIS.MLAT.CD", "DT.DIS.MLTC.CD"

    ids = DebtIDS()

    ids.load_data(
        indicators=[indicator1, indicator2], start_year=start_year, end_year=end_year
    )

    df = (
        ids.get_data()
        .loc[lambda d: d.counterpart_area != "World"]
        .assign(year=lambda d: d.year.dt.year)
    )

    if exclude_china_country:
        df = df.loc[lambda d: d.country != "China"]

    if exclude_china_counterpart:
        df = df.loc[lambda d: d.counterpart_area != "China"]

    if indicator == "multilateral" and only_mdbs:
        df = exclude_non_mdbs(df)

    df = (
        df.groupby(
            [c for c in df.columns if c not in ["value", "counterpart_area"]],
            as_index=False,
            dropna=False,
            observed=True,
        )["value"]
        .sum()
        .drop(columns=["series"])
    )

    # Reshape
    dfp = df.pivot(
        index=[c for c in df.columns if c not in ["value", "series_code"]],
        columns="series_code",
        values="value",
    ).reset_index()

    dfp["value"] = dfp[indicator1] - dfp[indicator2]

    dfp["iso_code"] = convert_id(
        dfp.country, from_type="regex", to_type="ISO3", not_found=pd.NA
    )

    if prices == "constant":
        dfp = to_constant(dfp)

    data = dfp.loc[lambda d: d.iso_code.notna()]

    data = data.groupby(["year"]).sum(numeric_only=True).div(1e6).round(1).reset_index()

    return data.filter(["year", "value"])


def export_bilateral():
    total = get_non_concessional_lending(
        exclude_china_country=False,
        exclude_china_counterpart=False,
        start_year=2017,
        end_year=2022,
    )
    no_china = get_non_concessional_lending(
        exclude_china_country=True,
        exclude_china_counterpart=True,
        start_year=2017,
        end_year=2022,
    )

    total.to_csv(config.Paths.output / "non_concessional_bilateral.csv", index=False)
    no_china.to_csv(
        config.Paths.output / "non_concessional_bilateral_excl_china.csv", index=False
    )

    total_stats = key_statistics(total, indicator="all_bilateral")
    no_china_stats = key_statistics(no_china, indicator="no_china_bilateral")

    export_json(
        config.Paths.output / "non_concessional_bilateral.json",
        total_stats | no_china_stats,
    )


def export_multilateral():
    total = get_non_concessional_lending(
        indicator="multilateral",
        exclude_china_country=False,
        start_year=2017,
        end_year=2022,
        only_mdbs=False,
    )

    exclude_china = get_non_concessional_lending(
        indicator="multilateral",
        exclude_china_country=True,
        start_year=2017,
        end_year=2022,
        only_mdbs=False,
    )

    total.to_csv(config.Paths.output / "non_concessional_multilateral.csv", index=False)
    exclude_china.to_csv(
        config.Paths.output / "non_concessional_multilateral_excl_china.csv",
        index=False,
    )

    total_stats = key_statistics(total, indicator="multilateral")
    exclude_china_stats = key_statistics(exclude_china, indicator="exclude_china")

    export_json(
        config.Paths.output / "non_concessional_multilateral.json",
        total_stats | exclude_china_stats,
    )


if __name__ == "__main__":
    export_bilateral()
    export_multilateral()
