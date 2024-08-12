import pandas as pd
from oda_data import read_crs
from pydeflate import deflate

from scripts.config import EXCLUDE_IDRC, EXCLUDE_CHINA, BILATERAL, DEV_COUNTRIES

INDICATORS: dict[str, str] = {
    "official_oda": "total_oda_official_definition",
    "total_net": "total_oda_bilateral_flow_net",
    "total_gross": "total_oda_flow_gross",
    "total_grants": "total_oda_grants_flow",
    "total_non_grants": "total_oda_non_grants_flow",
    "bilateral_net": "total_oda_bilateral_flow_net",
    "total_in_donor_refugees": "idrc_ge_linked",
    "bilateral_recipient_total_gross": "recipient_bilateral_flow_gross",
    "bilateral_recipient_total_net": "recipient_bilateral_flow_net",
    "bilateral_recipient_grants": "recipient_grants_flow",
    "bilateral_recipient_loans_gross": "recipient_loans_flow_gross",
    "bilateral_recipient_loans_net": "recipient_loans_flow_net",
    "bilateral_commitments": "bilateral_commitments",
}


REFUGEE_MODS: list[str] = ["H02", "H03", "H04", "H05", "H06"]


def to_constant(df: pd.DataFrame, base_year: int = 2019) -> pd.DataFrame:
    """Convert the values to constant prices"""
    df = deflate(
        df=df,
        base_year=base_year,
        deflator_source="oecd_dac",
        deflator_method="dac_deflator",
        exchange_source="oecd_dac",
        source_currency="USA",
        target_currency="USA",
        id_column="donor_code",
        id_type="DAC",
        date_column="year",
        source_column="usd_commitment",
        target_column="usd_commitment",
    )

    return df


def keep_oda_only(df: pd.DataFrame) -> pd.DataFrame:
    """Filter the data to only include ODA"""
    df = df.loc[lambda d: d["flow_code"].isin([11, 13, 19])]

    return df


def get_commitments_data(
    start_year: int = 2019,
    end_year: int = 2023,
    oda_only: bool = True,
    prices: str = "constant",
    base_year: int = 2019,
):
    """Get the total ODA for the given years"""

    grouper = [
        "year",
        "donor_code",
        "donor_name",
        "recipient_code",
        "recipient_name",
        "modality",
    ]

    df = read_crs(years=range(start_year, end_year + 1))

    if oda_only:
        df = keep_oda_only(df)

    if EXCLUDE_IDRC:
        df = df.loc[lambda d: ~d["modality"].isin(REFUGEE_MODS)]
        grouper = [c for c in grouper if c != "modality"]

    if EXCLUDE_CHINA:
        df = df.loc[lambda d: d["recipient_code"] != 730]

    df = df.groupby(grouper, as_index=False, dropna=False, observed=True)[
        ["usd_commitment"]
    ].sum()

    if prices == "constant":
        df = to_constant(df, base_year=base_year)

    return df.rename(columns={"usd_commitment": "value"})


def group_donors(df: pd.DataFrame) -> pd.DataFrame:
    """Group the data by donor"""

    grouper = [c for c in df.columns if c not in ["donor_code", "donor_name", "value"]]

    return df.groupby(grouper, as_index=False, dropna=False, observed=True)[
        "value"
    ].sum()


def group_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Group the data by indicator"""

    grouper = [c for c in df.columns if c not in ["indicator", "value"]]

    return df.groupby(grouper, as_index=False, dropna=False, observed=True)[
        "value"
    ].sum()


def group_recipients(df: pd.DataFrame) -> pd.DataFrame:
    grouper = [
        c for c in df.columns if c not in ["recipient_code", "recipient_name", "value"]
    ]

    return df.groupby(grouper, as_index=False, dropna=False, observed=True)[
        "value"
    ].sum()


def add_donor_name(df: pd.DataFrame) -> pd.DataFrame:
    df["donor_name"] = df["donor_code"].map(BILATERAL).fillna("donor_code")

    return df


def filter_dev_countries(df: pd.DataFrame) -> pd.DataFrame:
    if "recipient_code" in df.columns:
        df = df.loc[lambda d: d["recipient_code"].isin(DEV_COUNTRIES.keys())]

    return df
