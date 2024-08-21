import pandas as pd

from bblocks import WorldEconomicOutlook, set_bblocks_data_path, add_income_level_column
from pydeflate import deflate, set_pydeflate_path

from scripts import config

set_bblocks_data_path(config.Paths.raw_data)
set_pydeflate_path(config.Paths.raw_data)


def get_usd_gdp() -> pd.DataFrame:
    weo = WorldEconomicOutlook()
    weo.load_data(indicator=["NGDPD"])
    data = (
        weo.get_data().rename(columns={"value": "gdp_usd"}).drop(columns=["indicator"])
    )

    # from billion to usd
    data["gdp_usd"] = data["gdp_usd"] * 1e9

    return data


def gdp2usd(data: pd.DataFrame) -> pd.DataFrame:
    """
    Convert GDP data to USD
    """

    gdp = get_usd_gdp().assign(year=lambda d: d.year.dt.year)

    data = data.merge(gdp, on=["iso_code", "year"], how="left")

    data["value"] = data["value"] * data["gdp_usd"]

    data = data.drop(columns=["gdp_usd"])

    return data


def to_constant(df: pd.DataFrame, base_year: int = 2019) -> pd.DataFrame:
    """
    Convert data to constant USD
    """
    df = deflate(
        df=df,
        base_year=base_year,
        deflator_source="imf",
        deflator_method="gdp",
        exchange_source="imf",
        source_currency="USA",
        target_currency="USA",
        id_column="iso_code",
        id_type="ISO3",
        date_column="year",
        source_column="value",
        target_column="value",
    )

    return df


def exclude_china(data: pd.DataFrame) -> pd.DataFrame:
    return data.loc[lambda d: d.iso_code != "CHN"]


def exclude_high_income(data: pd.DataFrame) -> pd.DataFrame:
    data = add_income_level_column(data, id_column="iso_code", id_type="ISO3")
    return data.loc[lambda d: d.income_level != "High income"].drop(
        columns=["income_level"]
    )


def group_countries(data: pd.DataFrame) -> pd.DataFrame:

    grouper = [c for c in data.columns if c not in ["iso_code", "value"]]

    data = (
        data.groupby(grouper, dropna=False, observed=True)[["value"]]
        .sum()
        .reset_index()
    )

    return data
