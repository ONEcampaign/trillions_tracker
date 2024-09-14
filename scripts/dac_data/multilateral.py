from scripts import config
from scripts.dac_data.oda import get_oda_data
from scripts.dac_data.oof import get_oof_data
from scripts.dac_data.tools import INDICATORS, key_statistics
from scripts.tools import export_json

START_YEAR: int = 2017
END_YEAR: int = 2023

MULTI = [
    104,
    807,
    811,
    820,
    901,
    903,
    905,
    906,
    909,
    910,
    913,
    914,
    915,
    918,
    921,
    923,
    928,
    932,
    940,
    944,
    948,
    951,
    953,
    958,
    959,
    962,
    963,
    964,
    966,
    967,
    971,
    974,
    976,
    978,
    981,
    988,
    990,
    1011,
    1012,
    1013,
    1015,
    1016,
    1019,
    1020,
    1023,
    1024,
    1025,
    1037,
    1038,
    1039,
    1045,
    1046,
    1047,
    1048,
    1049,
    1050,
    1052,
    1053,
    1054,
    1055,
    1311,
    1312,
    1313,
    1401,
    1404,
    1406,
]


def mdb_oda(indicator: str):
    """Get the mdb ODA data (concessional financing)"""

    df = get_oda_data(
        indicator=INDICATORS[indicator],
        donors=config.MDBs,
        start_year=START_YEAR,
        end_year=END_YEAR,
    )

    return df


def mdb_non_concessional(flow_type: str = "usd_commitment"):
    """Get the mdb non-concessional ODA data"""

    df = get_oof_data(
        donors=MULTI,
        start_year=START_YEAR,
        end_year=END_YEAR,
        flow_type=flow_type,
        exclude_china=False,
        exclude_idrc=False,
        exclude_students=False,
        exclude_awareness=False,
    )

    return df


if __name__ == "__main__":

    # Concessional
    # indicator_disb = "bilateral_recipient_total_gross"
    # indicator_comm = "bilateral_commitments"
    # data_disb = mdb_oda(indicator=indicator_disb)
    # data_comm = mdb_oda(indicator=indicator_comm)
    # stats_disb = key_statistics(data_disb, indicator="gross_disbursements")
    # stats_comm = key_statistics(data_comm, indicator="commitments")

    # Non-concessional
    data_oof = mdb_non_concessional(flow_type="usd_disbursement")
    stats_oof = key_statistics(data_oof, indicator="non_concessional")

    # Save the data
    # data_disb.to_csv(
    #     config.Paths.output / "mdb_disbursements_concessional_constant_excl_China.csv",
    #     index=False,
    # )
    #
    # data_comm.to_csv(
    #     config.Paths.output / "mdb_commitments_concessional_constant_excl_China.csv",
    #     index=False,
    # )

    data_oof.to_csv(
        config.Paths.output
        / "mdb_commitments_non_concessional_constant_excl_China.csv",
        index=False,
    )

    # export_json(
    #     config.Paths.output / "mdb_stats_concessional_disbursements_oda.json",
    #     stats_disb,
    # )

    # export_json(
    #     config.Paths.output / "mdb_stats_concessional_commitments_oda.json", stats_comm
    # )

    export_json(config.Paths.output / "mdb_stats_non_concessional.json", stats_oof)
