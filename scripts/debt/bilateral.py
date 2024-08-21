import pandas as pd
from bblocks import set_bblocks_data_path, DebtIDS, add_iso_codes_column, convert_id

from scripts import config
from scripts.config import DRM_INDICATOR, EXCLUDE_CHINA
from scripts.dac_data.tools import key_statistics
from scripts.drm.tools import (
    gdp2usd,
    to_constant,
    exclude_china,
    group_countries,
    keep_emde_only,
)
from scripts.tools import export_json

set_bblocks_data_path(config.Paths.raw_data)


def get_non_concessional_lending(
    start_year: int = 2017,
    end_year: int = 2023,
    exclude_china_counterpart: bool = True,
    exclude_china_country: bool = True,
    prices: str = "constant",
) -> pd.DataFrame:

    indicators = ["DT.DIS.BLAT.CD", "DT.DIS.BLTC.CD"]
    ids = DebtIDS()

    ids.load_data(indicators=indicators, start_year=start_year, end_year=end_year)

    df = (
        ids.get_data()
        .loc[lambda d: d.counterpart_area != "World"]
        .assign(year=lambda d: d.year.dt.year)
    )

    if exclude_china_country:
        df = df.loc[lambda d: d.country != "China"]

    if exclude_china_counterpart:
        df = df.loc[lambda d: d.counterpart_area != "China"]

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

    dfp["value"] = dfp["DT.DIS.BLAT.CD"] - dfp["DT.DIS.BLTC.CD"]

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

    total_stats = key_statistics(total, indicator="all_bilateral")
    no_china_stats = key_statistics(no_china, indicator="no_china_bilateral")

    export_json(
        config.Paths.output / "non_concessional_bilateral.json",
        total_stats | no_china_stats,
    )


if __name__ == "__main__":

    export_bilateral()
