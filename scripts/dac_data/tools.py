import pandas as pd
from oda_data import read_crs, donor_groupings, read_dac1
from pydeflate import deflate

from scripts.config import (
    EXCLUDE_IDRC,
    EXCLUDE_CHINA,
    DEV_COUNTRIES,
    REFERENCE_YEAR,
    EXCLUDE_STUDENTS,
    EXCLUDE_AWARENESS,
)

INDICATORS: dict[str, str] = {
    "gross_disbursements": "gross_disbursements",
    "official_oda": "total_oda_official_definition",
    "core_oda": "total_oda_core",
    "multilateral_commitments": "multilateral_commitments",
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
    "students": "total_in_donor_students_ge_linked",
    "idrc": "idrc_ge_linked",
}

REFUGEE_MODS: list[str] = ["H02", "H03", "H04", "H05", "H06"]
STUDENT_MODS: list[str] = ["E01", "E02"]
AWARENESS_MODS: list[str] = ["H01"]


def to_constant(
    df: pd.DataFrame, base_year: int = 2019, column: str = "usd_commitment"
) -> pd.DataFrame:
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
        source_column=column,
        target_column=column,
    )

    return df


def keep_oda_only(df: pd.DataFrame) -> pd.DataFrame:
    """Filter the data to only include ODA"""
    df = df.loc[lambda d: d["flow_code"].isin([11, 13, 19])]

    return df


def keep_non_oda_only(df: pd.DataFrame) -> pd.DataFrame:
    """Filter the data to only include ODA"""
    df = df.loc[lambda d: ~d["flow_code"].isin([11, 13, 19])]

    return df


def get_multilateral_commitments(
    donors: list[int | str],
    start_year: int = 2019,
    end_year: int = 2023,
    prices: str = "constant",
    base_year: int = 2019,
):
    """Get the total ODA for the given years"""

    grouper = [
        "year",
        "donor_code",
        "donor_name",
    ]

    df = read_dac1(years=range(start_year, end_year + 1))

    df = df.loc[lambda d: d["donor_code"].isin(donors)]

    df = df.query(
        "aidtype_code == 2000 and flows_code == 1150 and amounttype_code=='A'"
    )

    df = (
        df.groupby(grouper, as_index=False, dropna=False, observed=True)[["value"]]
        .sum()
        .rename(columns={"value": "usd_commitment"})
    )

    if prices == "constant":
        df = to_constant(df, base_year=base_year)

    return df.rename(columns={"usd_commitment": "value"})


def get_commitments_data(
    donors: list[int | str],
    start_year: int = 2019,
    end_year: int = 2023,
    oda_only: bool = True,
    non_oda_only: bool = False,
    prices: str = "constant",
    base_year: int = 2019,
    exclude_china: bool = EXCLUDE_CHINA,
    exclude_idrc: bool = EXCLUDE_IDRC,
    exclude_students: bool = EXCLUDE_STUDENTS,
    exclude_awareness: bool = EXCLUDE_AWARENESS,
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

    df = df.loc[lambda d: d["donor_code"].isin(donors)]

    if oda_only and non_oda_only:
        raise ValueError("Cannot have both oda_only and non_oda_only as True")

    if oda_only:
        df = keep_oda_only(df)

    if non_oda_only:
        df = keep_non_oda_only(df)

    if exclude_idrc:
        df = df.loc[lambda d: ~d["modality"].isin(REFUGEE_MODS)]

    if exclude_students:
        df = df.loc[lambda d: ~d["modality"].isin(STUDENT_MODS)]

    if exclude_awareness:
        df = df.loc[lambda d: ~d["modality"].isin(AWARENESS_MODS)]

    if exclude_idrc or exclude_students or exclude_awareness:
        grouper = [c for c in grouper if c != "modality"]

    if exclude_china:
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


def group_recipients(df: pd.DataFrame) -> pd.DataFrame:
    grouper = [
        c for c in df.columns if c not in ["recipient_code", "recipient_name", "value"]
    ]

    return df.groupby(grouper, as_index=False, dropna=False, observed=True)[
        "value"
    ].sum()


def add_donor_name(df: pd.DataFrame) -> pd.DataFrame:
    df["donor_name"] = (
        df["donor_code"].map(donor_groupings()["all_official"]).fillna("donor_code")
    )

    return df


def filter_dev_countries(df: pd.DataFrame) -> pd.DataFrame:
    if "recipient_code" in df.columns:
        df = df.loc[lambda d: d["recipient_code"].isin(DEV_COUNTRIES.keys())]

    return df


def key_statistics(df: pd.DataFrame, indicator: str):
    total_latest = df.loc[lambda d: d.year == d.year.max()].value.sum()
    total_baseline = df.loc[lambda d: d.year == REFERENCE_YEAR].value.sum()
    change_usd = total_latest - total_baseline
    change_pct = change_usd / total_baseline

    return {
        indicator: {
            "total_latest": f"{total_latest / 1e3:.1f} billion",
            "total_baseline": f"{total_baseline / 1e3:.1f} billion",
            "change_usd": f"{change_usd / 1e3:.1f} billion",
            "change_pct": f"{change_pct:.1%}",
        }
    }
