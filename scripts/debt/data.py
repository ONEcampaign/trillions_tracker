import pandas as pd
from bblocks import set_bblocks_data_path, DebtIDS, convert_id

from scripts import config
from scripts.dac_data.tools import key_statistics
from scripts.drm.tools import (
    to_constant,
    keep_emde_only,
)
from scripts.tools import export_json

set_bblocks_data_path(config.Paths.raw_data)

NON_MDBs = [
    "Arab Monetary Fund",
    "Arab Fund for Economic & Social Development",
    "OPEC Fund for International Dev.",
    "Plata Basin Financial Dev. Fund",
    "International Finance Corporation",
    "African Export-Import Bank",
    "European Social Fund (ESF)",
    "European Development Fund (EDF)",
    "Nordic Investment Bank",
    "Arab African International Bank",
]


def exclude_non_mdbs(df: pd.DataFrame):
    return df.loc[lambda d: ~d.counterpart_area.isin(NON_MDBs)]


def get_non_concessional_lending(
    indicator: str = "bilateral",
    start_year: int = 2013,
    end_year: int = 2023,
    exclude_china_counterpart: bool = True,
    exclude_china_country: bool = True,
    only_mdbs: bool = True,
    prices: str = "constant",
) -> pd.DataFrame:

    if indicator == "bilateral":
        indicator1, indicator2 = "DT.DIS.BLAT.CD", "DT.DIS.BLTC.CD"
    else:
        indicator1, indicator2 = "DT.DIS.MLAT.CD", "DT.DIS.MLTC.CD"

    ids = DebtIDS()

    ids.load_data(
        indicators=[indicator1, indicator2], start_year=start_year, end_year=end_year
    )

    df = (
        ids.get_data()
        .loc[lambda d: d.counterpart_area != "World"]
        .assign(year=lambda d: d.year.dt.year)
    )

    if exclude_china_country:
        df = df.loc[lambda d: d.country != "China"]

    if exclude_china_counterpart:
        df = df.loc[lambda d: d.counterpart_area != "China"]

    if indicator == "multilateral" and only_mdbs:
        df = exclude_non_mdbs(df)

    df = (
        df.groupby(
            [c for c in df.columns if c not in ["value", "counterpart_area"]],
            as_index=False,
            dropna=False,
            observed=True,
        )["value"]
        .sum()
        .drop(columns=["series"])
    )

    # Reshape
    dfp = df.pivot(
        index=[c for c in df.columns if c not in ["value", "series_code"]],
        columns="series_code",
        values="value",
    ).reset_index()

    dfp["value"] = dfp[indicator1] - dfp[indicator2]

    dfp["iso_code"] = convert_id(
        dfp.country, from_type="regex", to_type="ISO3", not_found=pd.NA
    )

    if prices == "constant":
        dfp = to_constant(dfp)

    data = dfp.loc[lambda d: d.iso_code.notna()]

    data = data.groupby(["year"]).sum(numeric_only=True).div(1e6).round(1).reset_index()

    return data.filter(["year", "value"])


def export_bilateral():
    total = get_non_concessional_lending(
        exclude_china_country=False,
        exclude_china_counterpart=False,
        start_year=2013,
        end_year=2022,
    )
    no_china = get_non_concessional_lending(
        exclude_china_country=False,
        exclude_china_counterpart=True,
        start_year=2013,
        end_year=2022,
    )

    total.to_csv(
        config.Paths.output
        / "non_concessional_lending"
        / "non_concessional_bilateral.csv",
        index=False,
    )
    no_china.to_csv(
        config.Paths.output
        / "non_concessional_lending"
        / "non_concessional_bilateral_excl_china.csv",
        index=False,
    )

    total_stats = key_statistics(total, indicator="all_bilateral")
    no_china_stats = key_statistics(no_china, indicator="no_china_bilateral")

    export_json(
        config.Paths.output
        / "non_concessional_lending"
        / "non_concessional_bilateral.json",
        total_stats | no_china_stats,
    )


def export_multilateral():
    total = get_non_concessional_lending(
        indicator="multilateral",
        exclude_china_country=False,
        start_year=2013,
        end_year=2022,
        only_mdbs=False,
    )

    exclude_china = get_non_concessional_lending(
        indicator="multilateral",
        exclude_china_country=True,
        start_year=2013,
        end_year=2022,
        only_mdbs=False,
    )

    total.to_csv(
        config.Paths.output
        / "non_concessional_lending"
        / "non_concessional_multilateral.csv",
        index=False,
    )
    exclude_china.to_csv(
        config.Paths.output
        / "non_concessional_lending"
        / "non_concessional_multilateral_excl_china.csv",
        index=False,
    )

    total_stats = key_statistics(total, indicator="multilateral")
    exclude_china_stats = key_statistics(exclude_china, indicator="exclude_china")

    export_json(
        config.Paths.output
        / "non_concessional_lending"
        / "non_concessional_multilateral.json",
        total_stats | exclude_china_stats,
    )


def export_debt_oecd(
    indicator: str = "debt_service",
    start_year: int = 2015,
    end_year: int = 2025,
    prices: str = "constant",
    base_year: int | None = 2019,
    by_creditor: bool = False,
    by_debt_type: bool = False,
    only_emde: bool = True,
):
    suffix = f"{base_year}constant" if prices == "constant" else "current"
    suffix += "_by_creditor" if by_creditor else ""
    suffix += "_by_debt_type" if by_debt_type else ""
    suffix += "_emde_only" if only_emde else ""

    ids = DebtIDS()
    debt_service = {
        k: v.split(" ")[0] for k, v in ids.debt_service_indicators().items()
    }

    if indicator == "debt_service":
        indicators = list(debt_service)

    if indicator == "bilateral_non_concessional_debt_disbursements":
        indicators = ["DT.DIS.BLAT.CD", "DT.DIS.BLTC.CD"]

    if indicator == "multilateral_non_concessional_debt_disbursements":
        indicators = ["DT.DIS.MLAT.CD", "DT.DIS.MLTC.CD"]

    ids.load_data(indicators=indicators, start_year=start_year, end_year=end_year)

    df = (
        ids.get_data()
        .loc[lambda d: d.counterpart_area != "World"]
        .assign(
            year=lambda d: d.year.dt.year,
            value=lambda d: d.value / 1e6,
            units="USD million",
            prices=prices,
        )
    )

    if indicator == "debt_service":
        df = df.assign(debt_type=lambda d: d.series_code.map(debt_service))
    else:
        df["debt_type"] = df.series.str.split(" ").str[1].str.title()
        df = df.drop(columns=["series"])
        df = df.pivot(
            index=[c for c in df.columns if c not in ["value", "series_code"]],
            columns="series_code",
            values="value",
        ).reset_index()

        df["value"] = df[indicators[0]].fillna(0) - df[indicators[1]].fillna(0)
        df = df.loc[lambda d: d.value != 0]

        df = df.drop(columns=indicators)

    df["iso_code"] = convert_id(
        df.country, from_type="regex", to_type="ISO3", not_found=pd.NA
    )

    df = df.loc[lambda d: d.iso_code.notna()]

    df["counterpart_iso_code"] = convert_id(
        df.counterpart_area,
        from_type="regex",
        to_type="ISO3",
        not_found="",
        additional_mapping={
            "Korea, D.P.R. of": "PRK",
            "Neth. Antilles": "ANT",
            "Eastern & Southern African Trade & Dev. Bank (TDB)": "",
        },
    )

    if only_emde:
        df = keep_emde_only(df)

    if prices == "constant":
        df = to_constant(df, base_year=base_year)

    df = df.rename(
        columns={
            "counterpart_iso_code": "creditor_iso_code",
            "counterpart_area": "creditor",
        }
    )

    if not by_creditor:
        if not by_debt_type:
            df = (
                df.groupby(
                    ["year", "iso_code", "country", "prices", "units"],
                    observed=True,
                    dropna=False,
                )["value"]
                .sum()
                .reset_index()
            )
        else:
            df = (
                df.groupby(
                    ["year", "iso_code", "country", "debt_type", "prices", "units"],
                    observed=True,
                    dropna=False,
                )["value"]
                .sum()
                .reset_index()
            )

    df = df.filter(
        [
            "year",
            "iso_code",
            "country",
            "creditor_iso_code",
            "creditor",
            "debt_type",
            "prices",
            "units",
            "value",
        ]
    )

    end_year = df.loc[lambda d: (d.value != 0) & d.value.notna()].year.max()
    suffix += f"_{start_year}_{end_year}"

    df.to_csv(
        config.Paths.output / "oecd" / f"{indicator}_{suffix}.csv",
        index=False,
    )


def export_oecd_versions(
    indicator: str, start_year: int = 2015, end_year: int = 2025, base_year: int = 2015
) -> None:
    export_debt_oecd(
        indicator=indicator,
        start_year=start_year,
        end_year=end_year,
        prices="constant",
        base_year=base_year,
        by_creditor=False,
        by_debt_type=False,
        only_emde=False,
    )
    export_debt_oecd(
        indicator=indicator,
        start_year=start_year,
        end_year=end_year,
        prices="current",
        base_year=None,
        by_creditor=False,
        by_debt_type=False,
        only_emde=False,
    )

    export_debt_oecd(
        indicator=indicator,
        start_year=start_year,
        end_year=end_year,
        prices="constant",
        base_year=base_year,
        by_creditor=False,
        by_debt_type=True,
        only_emde=False,
    )
    export_debt_oecd(
        indicator=indicator,
        start_year=start_year,
        end_year=end_year,
        prices="current",
        base_year=None,
        by_creditor=False,
        by_debt_type=True,
        only_emde=False,
    )

    export_debt_oecd(
        indicator=indicator,
        start_year=start_year,
        end_year=end_year,
        prices="constant",
        base_year=base_year,
        by_creditor=True,
        by_debt_type=True,
        only_emde=False,
    )
    export_debt_oecd(
        indicator=indicator,
        start_year=start_year,
        end_year=end_year,
        prices="current",
        base_year=None,
        by_creditor=True,
        by_debt_type=True,
        only_emde=False,
    )


if __name__ == "__main__":
    export_bilateral()
    export_multilateral()
    export_oecd_versions(indicator="debt_service", base_year=2015)
    export_oecd_versions(
        indicator="bilateral_non_concessional_debt_disbursements", base_year=2015
    )
    export_oecd_versions(
        indicator="multilateral_non_concessional_debt_disbursements", base_year=2015
    )
