import pandas as pd
from oda_data import set_data_path, donor_groupings, ODAData, recipient_groupings

from scripts import config
from scripts.logger import logger

EXCLUDE_CHINA = True
BILATERAL = donor_groupings()["all_bilateral"]
DEV_COUNTRIES = {
    k: v
    for k, v in recipient_groupings()["all_developing_countries_regions"].items()
    if k != 730
}
set_data_path(config.Paths.raw_data)


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
}

CRS: str = "crs_bilateral_all_flows_disbursement_gross"


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

    grouper = [c for c in df.columns if c not in ["recipient_code", "value"]]

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


def get_oda_data(
    indicator: str,
    start_year: int = 2019,
    end_year: int = 2023,
    prices: str = "constant",
    base_year: int = 2019,
    by_donor: bool = False,
    by_recipient: bool = False,
) -> pd.DataFrame:
    """Get the total ODA for the given years"""

    # Create ODA object
    oda = ODAData(
        years=range(start_year, end_year + 1),
        donors=list(BILATERAL.keys()),
        prices=prices,
        base_year=base_year,
    )

    # Load the indicator
    oda.load_indicator(indicator)

    # Get the indicator data, add donor_name, filter dev countries
    df = oda.get_data().pipe(add_donor_name).pipe(filter_dev_countries)

    # Group the data as requested
    if not by_donor:
        df = group_donors(df)

    if not by_recipient:
        df = group_recipients(df)

    return df


if __name__ == "__main__":
    data = get_oda_data(
        indicator=INDICATORS["official_oda"],
        start_year=2019,
        end_year=2023,
        # by_donor=True,
        # by_recipient=True,
    )
