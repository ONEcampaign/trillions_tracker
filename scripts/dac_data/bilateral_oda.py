from scripts import config
from scripts.dac_data.oda import get_oda_data
from scripts.dac_data.oof import get_oof_data
from scripts.dac_data.tools import INDICATORS, key_statistics
from scripts.tools import export_json

START_YEAR: int = 2017
END_YEAR: int = 2023


def bilateral_oda(indicator: str):
    """Get the bilateral ODA data"""

    df = get_oda_data(
        indicator=INDICATORS[indicator],
        donors=list(config.BILATERAL),
        start_year=START_YEAR,
        end_year=END_YEAR,
    )

    return df


def bilateral_non_concessional():
    """Get the bilateral non-concessional ODA data"""

    df = get_oof_data(
        donors=list(config.BILATERAL),
        start_year=START_YEAR,
        end_year=END_YEAR,
    )

    return df


if __name__ == "__main__":
    # Concessional
    indicator_disb = "bilateral_recipient_total_gross"
    indicator_comm = "bilateral_commitments"
    data_disb = bilateral_oda(indicator=indicator_disb)
    data_comm = bilateral_oda(indicator=indicator_comm)
    stats_disb = key_statistics(data_disb, indicator=indicator_disb)
    stats_comm = key_statistics(data_comm, indicator=indicator_comm)

    # Non-concessional
    data_oof = bilateral_non_concessional()
    stats_oof = key_statistics(data_oof, indicator="non_concessional")

    # Save the data
    data_disb.to_csv(
        config.Paths.output / "bilateral_disbursements_oda_constant_excl_China.csv",
        index=False,
    )

    data_comm.to_csv(
        config.Paths.output / "bilateral_commitments_oda_constant_excl_China.csv",
        index=False,
    )

    data_oof.to_csv(
        config.Paths.output / "bilateral_non_concessional_constant_excl_China.csv",
        index=False,
    )

    export_json(
        config.Paths.output / "key_stats_bilateral_disbursements_oda.json", stats_disb
    )

    export_json(
        config.Paths.output / "key_stats_bilateral_commitments_oda.json", stats_comm
    )

    export_json(
        config.Paths.output / "key_stats_bilateral_non_concessional.json", stats_oof
    )
