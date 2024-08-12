from pathlib import Path

from oda_data import donor_groupings, recipient_groupings


class Paths:
    """Class to store the paths to the data and output folders."""

    project = Path(__file__).resolve().parent.parent
    raw_data = project / "raw_data"
    output = project / "output"
    scripts = project / "scripts"


REFERENCE_YEAR: int = 2019

EXCLUDE_CHINA = True
EXCLUDE_IDRC = True

BILATERAL = donor_groupings()["all_bilateral"]

DEV_COUNTRIES = {
    k: v
    for k, v in recipient_groupings()["all_developing_countries_regions"].items()
    if k != 730
}

MDBs = [
    901,
    902,
    903,
    905,
    906,
    907,
    909,
    913,
    914,
    915,
    953,
    958,
    976,
    979,
    981,
    990,
    1013,
    1015,
    1019,
    1014,
]
