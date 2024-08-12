import pandas as pd

from scripts import config
from scripts.dac_data.oda import get_oda_data
from scripts.dac_data.tools import INDICATORS
from scripts.tools import export_json

START_YEAR: int = 2017
END_YEAR: int = 2023

REFERENCE_YEAR: int = 2019


def key_statistics(df: pd.DataFrame, indicator: str):

    total_latest = df.loc[lambda d: d.year == d.year.max()].value.sum()
    total_baseline = df.loc[lambda d: d.year == REFERENCE_YEAR].value.sum()
    change_usd = total_latest - total_baseline
    change_pct = change_usd / total_baseline

    return {
        indicator: {
            "total_latest": f"{total_latest/1e3:.1f} billion",
            "total_baseline": f"{total_baseline/1e3:.1f} billion",
            "change_usd": f"{change_usd/1e3:.1f} billion",
            "change_pct": f"{change_pct:.1%}",
        }
    }


def bilateral_oda(indicator: str):
    """Get the bilateral ODA data"""

    df = get_oda_data(
        indicator=INDICATORS[indicator],
        donors=list(config.BILATERAL),
        start_year=START_YEAR,
        end_year=END_YEAR,
    )

    return df


if __name__ == "__main__":

    indicator_disb = "bilateral_recipient_total_gross"
    indicator_comm = "bilateral_commitments"
    data_disb = bilateral_oda(indicator=indicator_disb)
    data_comm = bilateral_oda(indicator=indicator_comm)
    stats_disb = key_statistics(data_disb, indicator=indicator_disb)
    stats_comm = key_statistics(data_comm, indicator=indicator_comm)

    data_disb.to_csv(
        config.Paths.output / "bilateral_disbursements_oda_constant_excl_China.csv",
        index=False,
    )

    data_comm.to_csv(
        config.Paths.output / "bilateral_commitments_oda_constant_excl_China.csv",
        index=False,
    )

    export_json(
        config.Paths.output / "key_stats_bilateral_disbursements_oda.json", stats_disb
    )

    export_json(
        config.Paths.output / "key_stats_bilateral_commitments_oda.json", stats_comm
    )
