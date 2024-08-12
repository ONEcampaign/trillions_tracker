import pandas as pd
from bblocks import WorldEconomicOutlook, set_bblocks_data_path

from scripts import config
from scripts.config import DRM_INDICATOR, EXCLUDE_CHINA
from scripts.drm.tools import gdp2usd, to_constant, exclude_china, group_countries

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
    prices: str = "constant",
    base_year: int = 2019,
) -> pd.DataFrame:
    """DRM data for the specified indicator, as millions of USD."""

    weo = WorldEconomicOutlook()
    weo.load_data(indicator=indicator)

    # As percent of GDP
    data = weo.get_data().assign(
        year=lambda d: d.year.dt.year, value=lambda d: d.value / 100
    )

    data = data.loc[lambda d: d.year.between(start_year, end_year)]

    # As USD
    data = gdp2usd(data)

    if prices == "constant":
        data = to_constant(data, base_year=base_year)

    if EXCLUDE_CHINA:
        data = exclude_china(data)

    if not by_country:
        data = group_countries(data)

    return data.assign(value=lambda d: (d.value.astype(float) / 1e6).round(1))


if __name__ == "__main__":
    df = get_drm(indicator=INDICATORS[DRM_INDICATOR], start_year=2017, end_year=2029)
