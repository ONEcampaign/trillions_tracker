"""Non-concessional"""

import pandas as pd
from oda_data import set_data_path
from pydeflate import set_pydeflate_path

from scripts import config
from scripts.config import BILATERAL
from scripts.dac_data.tools import (
    get_commitments_data,
    group_donors,
    group_recipients,
)

set_data_path(config.Paths.raw_data)
set_pydeflate_path(config.Paths.raw_data)


def get_oof_data(
    donors: list[str],
    start_year: int = 2019,
    end_year: int = 2023,
    prices: str = "constant",
    base_year: int = 2019,
    by_donor: bool = False,
    by_recipient: bool = False,
) -> pd.DataFrame:
    """Get the total ODA for the given years"""

    df = get_commitments_data(
        donors=donors,
        start_year=start_year,
        end_year=end_year,
        prices=prices,
        base_year=base_year,
        oda_only=False,
        non_oda_only=True,
    )

    # Group the data as requested
    if not by_donor:
        df = group_donors(df)

    if not by_recipient:
        df = group_recipients(df)

    return df


if __name__ == "__main__":
    data = get_oof_data(
        start_year=2017,
        end_year=2023,
        donors=BILATERAL,
    )
