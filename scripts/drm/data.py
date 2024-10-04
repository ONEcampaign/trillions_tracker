import pandas as pd
from bblocks import WorldEconomicOutlook, set_bblocks_data_path

from scripts import config
from scripts.config import DRM_INDICATOR, EXCLUDE_CHINA
from scripts.dac_data.tools import key_statistics
from scripts.drm.tools import (
    gdp2usd,
    to_constant,
    exclude_china,
    group_countries,
    keep_emde_only,
)
from scripts.tools import export_json

set_bblocks_data_path(config.Paths.raw_data)

INDICATORS: dict = {
    "expenditure": "GGX_NGDP",
    "revenue": "GGR_NGDP",
}


def get_drm(
    indicator: str,
    start_year: int,
    end_year: int,
    by_country: bool = False,
    only_emde: bool = True,
    prices: str = "constant",
    base_year: int = 2019,
    exclude_china_data: bool = EXCLUDE_CHINA,
    keep_metadata: bool = False,
) -> pd.DataFrame:
    """DRM data for the specified indicator, as millions of USD."""

    weo = WorldEconomicOutlook(year=2024, release=1)
    weo.load_data(indicator=indicator)

    # As percent of GDP
    data = weo.get_data(keep_metadata=keep_metadata).assign(
        year=lambda d: d.year.dt.year, value=lambda d: d.value / 100
    )

    # Filter years
    data = data.loc[lambda d: d.year.between(start_year, end_year)]

    if only_emde:
        # Filter countries
        data = keep_emde_only(data)

    # As USD
    data = gdp2usd(data)

    if prices == "constant":
        data = to_constant(data, base_year=base_year)

    if exclude_china_data:
        data = exclude_china(data)

    if not by_country:
        data = group_countries(data)

    return data.assign(value=lambda d: (d.value.astype(float) / 1e6).round(3))


def export_drm_data(exclude_china_data: bool = False):
    df = get_drm(
        indicator=INDICATORS[DRM_INDICATOR],
        start_year=2013,
        end_year=2022,
        exclude_china_data=exclude_china_data,
    )

    suffix = "_excl_China" if exclude_china_data else ""

    stats = key_statistics(df, "drm", max_year=2022)

    df.to_csv(
        config.Paths.output / "drm" / f"domestic_revenues_constant{suffix}.csv",
        index=False,
    )

    export_json(
        config.Paths.output / "drm" / f"stats_domestic_revenues_constant{suffix}.json",
        stats,
    )


def export_drm_oecd(
    start_year: int = 2015,
    end_year: int = 2028,
    prices: str = "constant",
    base_year: int = 2019,
    only_emde: bool = True,
):
    suffix = f"constant_{base_year}" if prices == "constant" else "current"
    suffix += "_emde" if only_emde else ""

    df = get_drm(
        indicator=INDICATORS[DRM_INDICATOR],
        start_year=start_year,
        end_year=end_year,
        by_country=True,
        only_emde=only_emde,
        exclude_china_data=False,
        prices=prices,
        base_year=base_year,
        keep_metadata=True,
    )

    df = df.filter(
        ["year", "entity_name", "iso_code", "estimate", "indicator_name", "value"]
    ).assign(units="USD million")

    df.to_csv(
        config.Paths.output / "oecd" / f"domestic_revenues_{suffix}.csv",
        index=False,
    )


if __name__ == "__main__":
    # export_drm_data(exclude_china_data=False)
    # export_drm_data(exclude_china_data=True)
    export_drm_oecd(base_year=2015)
    export_drm_oecd(only_emde=False, base_year=2015)
    export_drm_oecd(prices="current", base_year=None)
    export_drm_oecd(prices="current", base_year=None, only_emde=False)
