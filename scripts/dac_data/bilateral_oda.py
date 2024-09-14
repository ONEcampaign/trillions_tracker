import pandas as pd

from scripts import config
from scripts.dac_data.oda import get_oda_data
from scripts.dac_data.oof import get_oof_data
from scripts.dac_data.tools import INDICATORS, key_statistics
from scripts.tools import export_json

START_YEAR: int = 2017
END_YEAR: int = 2023


def bilateral_oda(
    indicator: str,
    exclude_china: bool = True,
    exclude_idrc: bool = True,
    exclude_students: bool = True,
    exclude_awareness: bool = True,
):
    """Get the bilateral ODA data"""

    df = get_oda_data(
        indicator=INDICATORS[indicator],
        donors=list(config.BILATERAL),
        start_year=START_YEAR,
        end_year=END_YEAR,
        exclude_china=exclude_china,
        exclude_idrc=exclude_idrc,
        exclude_students=exclude_students,
        exclude_awareness=exclude_awareness,
    )

    return df


def bilateral_non_concessional(
    exclude_china=True,
    exclude_idrc=True,
    exclude_awareness=True,
    exclude_students=True,
):
    """Get the bilateral non-concessional ODA data"""

    df = get_oof_data(
        donors=list(config.BILATERAL),
        start_year=START_YEAR,
        end_year=END_YEAR,
        exclude_china=exclude_china,
        exclude_idrc=exclude_idrc,
        exclude_awareness=exclude_awareness,
        exclude_students=exclude_students,
    )

    return df


def export_bilateral_commitments_versions():
    indicator_comm = "bilateral_commitments"

    data_comm_total = bilateral_oda(
        indicator=indicator_comm,
        exclude_china=True,
        exclude_idrc=False,
        exclude_awareness=False,
        exclude_students=False,
    )
    stats_comm_total = key_statistics(data_comm_total, indicator=indicator_comm)

    data_comm_core = bilateral_oda(
        indicator=indicator_comm,
        exclude_china=True,
        exclude_idrc=True,
        exclude_awareness=True,
        exclude_students=True,
    )

    stats_comm_core = key_statistics(data_comm_core, indicator=indicator_comm)

    data_comm_total.to_csv(
        config.Paths.output / "total_bilateral_commitments_oda_constant_excl_China.csv",
        index=False,
    )

    export_json(
        config.Paths.output / "total_key_stats_bilateral_commitments_oda.json",
        stats_comm_total,
    )

    data_comm_core.to_csv(
        config.Paths.output / "core_bilateral_commitments_oda_constant_excl_China.csv",
        index=False,
    )

    export_json(
        config.Paths.output / "core_key_stats_bilateral_commitments_oda.json",
        stats_comm_core,
    )


def export_all_donors_gross_disbursements(exclude_china: bool = True):
    indicator_comm = "gross_disbursements"
    suffix = "_excl_China" if exclude_china else ""

    gross_disbursements = bilateral_oda(
        indicator=indicator_comm,
        exclude_china=exclude_china,
    )
    stats_gross_disbursements_total = key_statistics(
        gross_disbursements, indicator=indicator_comm
    )

    students = bilateral_oda(indicator="students")
    idrc = bilateral_oda(indicator="idrc")

    in_donor = (
        pd.concat([students, idrc], ignore_index=True)
        .groupby(["year", "prices"], as_index=False, dropna=False, observed=True)[
            "value"
        ]
        .sum()
    )

    in_donor_stats = key_statistics(in_donor, indicator="in_donor")

    gross_disbursements.to_csv(
        config.Paths.output
        / "oda"
        / f"total_gross_disbursements_constant_oda{suffix}.csv",
        index=False,
    )

    in_donor.to_csv(
        config.Paths.output / "oda" / "in_donor_constant_oda.csv",
        index=False,
    )

    export_json(
        config.Paths.output
        / "oda"
        / f"total_gross_disbursements_constant_oda{suffix}.json",
        stats_gross_disbursements_total | in_donor_stats,
    )


def export_multilateral():
    indicator = "multilateral_commitments"
    data_comm_total = bilateral_oda(
        indicator=indicator,
        exclude_china=True,
        exclude_idrc=False,
        exclude_awareness=False,
        exclude_students=False,
    )
    stats_comm_total = key_statistics(data_comm_total, indicator=indicator)

    data_comm_total.to_csv(
        config.Paths.output / "core_multilateral_commitments_oda.csv",
        index=False,
    )

    export_json(
        config.Paths.output / "key_stats_core_multilateral_commitments_oda.json",
        stats_comm_total,
    )


def export_oof_bilateral_versions():
    data_oof_total = bilateral_non_concessional(
        exclude_china=True,
        exclude_idrc=False,
        exclude_awareness=False,
        exclude_students=False,
    )
    stats_oof_total = key_statistics(data_oof_total, indicator="non_concessional")

    data_oof_core = bilateral_non_concessional(
        exclude_china=True,
        exclude_idrc=True,
        exclude_awareness=True,
        exclude_students=True,
    )
    stats_oof_core = key_statistics(data_oof_core, indicator="non_concessional")

    data_oof_total.to_csv(
        config.Paths.output
        / "total_bilateral_non_concessional_constant_excl_China.csv",
        index=False,
    )

    export_json(
        config.Paths.output / "total_key_stats_bilateral_non_concessional.json",
        stats_oof_total,
    )

    data_oof_core.to_csv(
        config.Paths.output / "core_bilateral_non_concessional_constant_excl_China.csv",
        index=False,
    )

    export_json(
        config.Paths.output / "core_key_stats_bilateral_non_concessional.json",
        stats_oof_core,
    )


if __name__ == "__main__":
    # gross disbursements
    export_all_donors_gross_disbursements(exclude_china=True)
    export_all_donors_gross_disbursements(exclude_china=False)

    # Concessional
    # export_bilateral_commitments_versions()

    # Non-concessional
    # export_oof_bilateral_versions()

    # Multi
    # export_multilateral()
