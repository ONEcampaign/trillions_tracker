from scripts import config
from scripts.dac_data.oda import get_oda_data
from scripts.dac_data.oof import get_oof_data
from scripts.dac_data.tools import INDICATORS, key_statistics
from scripts.tools import export_json

START_YEAR: int = 2017
END_YEAR: int = 2023


def mdb_oda(indicator: str):
    """Get the mdb ODA data (concessional financing)"""

    df = get_oda_data(
        indicator=INDICATORS[indicator],
        donors=config.MDBs,
        start_year=START_YEAR,
        end_year=END_YEAR,
    )

    return df


def mdb_non_concessional():
    """Get the mdb non-concessional ODA data"""

    df = get_oof_data(
        donors=config.MDBs,
        start_year=START_YEAR,
        end_year=END_YEAR,
    )

    return df


if __name__ == "__main__":

    # Concessional
    indicator_disb = "bilateral_recipient_total_gross"
    indicator_comm = "bilateral_commitments"
    data_disb = mdb_oda(indicator=indicator_disb)
    data_comm = mdb_oda(indicator=indicator_comm)
    stats_disb = key_statistics(data_disb, indicator="gross_disbursements")
    stats_comm = key_statistics(data_comm, indicator="commitments")

    # Non-concessional
    data_oof = mdb_non_concessional()
    stats_oof = key_statistics(data_oof, indicator="non_concessional")

    # Save the data
    data_disb.to_csv(
        config.Paths.output / "mdb_disbursements_concessional_constant_excl_China.csv",
        index=False,
    )

    data_comm.to_csv(
        config.Paths.output / "mdb_commitments_concessional_constant_excl_China.csv",
        index=False,
    )

    data_oof.to_csv(
        config.Paths.output
        / "mdb_commitments_non_concessional_constant_excl_China.csv",
        index=False,
    )

    export_json(
        config.Paths.output / "mdb_stats_concessional_disbursements_oda.json",
        stats_disb,
    )

    export_json(
        config.Paths.output / "mdb_stats_concessional_commitments_oda.json", stats_comm
    )

    export_json(config.Paths.output / "mdb_stats_non_concessional.json", stats_oof)
