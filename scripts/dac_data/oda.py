import pandas as pd
from oda_data import set_data_path, ODAData
from pydeflate import set_pydeflate_path

from scripts import config
from scripts.config import BILATERAL
from scripts.dac_data.tools import (
    get_commitments_data,
    group_donors,
    group_recipients,
    add_donor_name,
    filter_dev_countries,
)

set_data_path(config.Paths.raw_data)
set_pydeflate_path(config.Paths.raw_data)


def get_oda_data(
    indicator: str,
    donors: list[str],
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
        donors=donors,
        prices=prices,
        base_year=base_year,
    )

    if indicator == "bilateral_commitments":
        df = get_commitments_data(
            start_year=start_year,
            end_year=end_year,
            prices=prices,
            base_year=base_year,
            oda_only=True,
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
    data = get_oda_data(
        indicator="bilateral_commitments",
        start_year=2017,
        end_year=2023,
        donors=list(BILATERAL),
    )
