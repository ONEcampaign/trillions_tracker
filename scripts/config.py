from pathlib import Path

from oda_data import donor_groupings, recipient_groupings


class Paths:
    """Class to store the paths to the data and output folders."""

    project = Path(__file__).resolve().parent.parent
    raw_data = project / "raw_data"
    output = project / "output"
    scripts = project / "scripts"


EXCLUDE_CHINA = True
EXCLUDE_IDRC = True

BILATERAL = donor_groupings()["all_bilateral"]

DEV_COUNTRIES = {
    k: v
    for k, v in recipient_groupings()["all_developing_countries_regions"].items()
    if k != 730
}
