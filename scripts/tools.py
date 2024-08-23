import json
from pathlib import Path

import pandas as pd
from bblocks import WorldEconomicOutlook, set_bblocks_data_path

from scripts import config

set_bblocks_data_path(config.Paths.raw_data)


def export_json(path: Path, data: dict):
    """Export a dictionary to a JSON file"""
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def get_usd_deflator() -> pd.DataFrame:
    weo = WorldEconomicOutlook()

    weo.load_data(indicator=["NGDP_D"])
    data = (
        weo.get_data()
        .assign(year=lambda d: d.year.dt.year)
        .rename(columns={"value": "deflator"})
        .loc[lambda d: d.year.between(2019, 2024)]
        .loc[lambda d: d.iso_code == "USA"]
    )

    d2019 = data.loc[lambda d: d.year == 2019, "deflator"].values[0]

    data["deflator"] = round(data["deflator"] / d2019, 4)

    return data


if __name__ == "__main__":
    deflator = get_usd_deflator()
    deflator.to_csv(config.Paths.output / "usd_deflator.csv", index=False)
