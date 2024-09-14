import pandas as pd
from oda_data import set_data_path, ODAData, read_dac2a, read_dac1
from pydeflate import set_pydeflate_path

from scripts import config
from scripts.config import BILATERAL
from scripts.dac_data.tools import (
    get_crs_data,
    group_donors,
    group_recipients,
    add_donor_name,
    filter_dev_countries,
    get_multilateral_commitments,
    to_constant,
)

set_data_path(config.Paths.raw_data)
set_pydeflate_path(config.Paths.raw_data)


def get_dac2a_data(
    start_year: int = 2019,
    end_year: int = 2023,
    prices: str = "constant",
    base_year: int = 2019,
    exclude_china: bool = True,
) -> pd.DataFrame:

    agg_donors = [20001, 20002, 20006]
    aidtype = 240
    data_type_code = "A"
    recipients = [10100, 730]

    oda = read_dac2a(years=range(start_year, end_year + 1))
    oda = (
        oda.loc[lambda d: d.donor_code.isin(agg_donors)]
        .loc[lambda d: d.aidtype_code == aidtype]
        .loc[lambda d: d.data_type_code == data_type_code]
        .loc[lambda d: d.recipient_code.isin(recipients)]
        .drop(columns="recipient_name")
    )

    if prices == "constant":
        oda = to_constant(oda, base_year=base_year, column="value")

    if exclude_china:
        oda = oda.pivot(
            index=[c for c in oda.columns if c not in ["value", "recipient_code"]],
            columns="recipient_code",
            values="value",
        )

        oda["value"] = oda[10100] - oda[730]
        oda = oda.drop(columns=[10100, 730]).reset_index()

    else:
        oda = oda.loc[lambda d: d.recipient_code == 10100].drop(
            columns="recipient_code"
        )

    return oda.filter(["year", "donor_code", "donor_name", "value"])


def get_oda_data(
    indicator: str,
    donors: list[str],
    start_year: int = 2019,
    end_year: int = 2023,
    prices: str = "constant",
    base_year: int = 2019,
    by_donor: bool = False,
    by_recipient: bool = False,
    exclude_china: bool = True,
    exclude_idrc: bool = True,
    exclude_students: bool = True,
    exclude_awareness: bool = True,
) -> pd.DataFrame:
    """Get the total ODA for the given years"""

    # Create ODA object
    oda = ODAData(
        years=range(start_year, end_year + 1),
        donors=donors,
        prices=prices,
        base_year=base_year,
    )

    if indicator == "bilateral_commitments":
        df = get_crs_data(
            donors=donors,
            start_year=start_year,
            end_year=end_year,
            oda_only=True,
            prices=prices,
            base_year=base_year,
            exclude_china=exclude_china,
            exclude_idrc=exclude_idrc,
            exclude_students=exclude_students,
            exclude_awareness=exclude_awareness,
        )
    elif indicator == "multilateral_commitments":
        df = get_multilateral_commitments(
            donors=donors,
            start_year=start_year,
            end_year=end_year,
            prices=prices,
            base_year=base_year,
        )
    elif indicator == "gross_disbursements":
        df = get_dac2a_data(
            start_year=start_year,
            end_year=end_year,
            prices=prices,
            base_year=base_year,
            exclude_china=exclude_china,
        )

    else:
        # Load the indicator
        oda.load_indicator(indicator)
        df = oda.get_data().pipe(add_donor_name).pipe(filter_dev_countries)

    # Group the data as requested
    if not by_donor:
        df = group_donors(df)

    if not by_recipient:
        df = group_recipients(df)

    return df


if __name__ == "__main__":
    ...
    # data = get_oda_data(
    #     indicator="gross_disbursements",
    #     start_year=2017,
    #     end_year=2023,
    #     donors=list(BILATERAL),
    #     by_donor=True,
    # )
