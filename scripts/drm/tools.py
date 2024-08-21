import pandas as pd

from bblocks import (
    WorldEconomicOutlook,
    set_bblocks_data_path,
    add_income_level_column,
    add_iso_codes_column,
)
from pydeflate import deflate, set_pydeflate_path

from scripts import config

set_bblocks_data_path(config.Paths.raw_data)
set_pydeflate_path(config.Paths.raw_data)


def get_usd_gdp() -> pd.DataFrame:
    weo = WorldEconomicOutlook()
    weo.load_data(indicator=["NGDPD"])
    data = (
        weo.get_data().rename(columns={"value": "gdp_usd"}).drop(columns=["indicator"])
    )

    # from billion to usd
    data["gdp_usd"] = data["gdp_usd"] * 1e9

    return data


def gdp2usd(data: pd.DataFrame) -> pd.DataFrame:
    """
    Convert GDP data to USD
    """

    gdp = get_usd_gdp().assign(year=lambda d: d.year.dt.year)

    data = data.merge(gdp, on=["iso_code", "year"], how="left")

    data["value"] = data["value"] * data["gdp_usd"]

    data = data.drop(columns=["gdp_usd"])

    return data


def to_constant(df: pd.DataFrame, base_year: int = 2019) -> pd.DataFrame:
    """
    Convert data to constant USD
    """
    df = deflate(
        df=df,
        base_year=base_year,
        deflator_source="imf",
        deflator_method="gdp",
        exchange_source="imf",
        source_currency="USA",
        target_currency="USA",
        id_column="iso_code",
        id_type="ISO3",
        date_column="year",
        source_column="value",
        target_column="value",
    )

    return df


def exclude_china(data: pd.DataFrame) -> pd.DataFrame:
    return data.loc[lambda d: d.iso_code != "CHN"]


def keep_emde_only(data: pd.DataFrame) -> pd.DataFrame:
    iso_list_to_keep = imf_emde()
    data = data.loc[lambda d: d.iso_code.isin(iso_list_to_keep)]
    return data


def group_countries(data: pd.DataFrame) -> pd.DataFrame:

    grouper = [c for c in data.columns if c not in ["iso_code", "value"]]

    data = (
        data.groupby(grouper, dropna=False, observed=True)[["value"]]
        .sum()
        .reset_index()
    )

    return data


def imf_emde():
    countries = [
        "Afghanistan",
        "Albania",
        "Algeria",
        "Angola",
        "Antigua and Barbuda",
        "Argentina",
        "Armenia",
        "Aruba",
        "Azerbaijan",
        "The Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belize",
        "Benin",
        "Bhutan",
        "Bolivia",
        "Bosnia and Herzegovina",
        "Botswana",
        "Brazil",
        "Brunei Darussalam",
        "Bulgaria",
        "Burkina Faso",
        "Burundi",
        "Cabo Verde",
        "Cambodia",
        "Cameroon",
        "Central African Republic",
        "Chad",
        "Chile",
        "China",
        "Colombia",
        "Comoros",
        "Democratic Republic of the Congo",
        "Republic of Congo",
        "Costa Rica",
        "Côte d'Ivoire",
        "Djibouti",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Eritrea",
        "Eswatini",
        "Ethiopia",
        "Fiji",
        "Gabon",
        "The Gambia",
        "Georgia",
        "Ghana",
        "Grenada",
        "Guatemala",
        "Guinea",
        "Guinea-Bissau",
        "Guyana",
        "Haiti",
        "Honduras",
        "Hungary",
        "India",
        "Indonesia",
        "Iran",
        "Iraq",
        "Jamaica",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Kiribati",
        "Kosovo",
        "Kuwait",
        "Kyrgyz Republic",
        "Lao P.D.R.",
        "Lebanon",
        "Lesotho",
        "Liberia",
        "Libya",
        "Madagascar",
        "Malawi",
        "Malaysia",
        "Maldives",
        "Mali",
        "Marshall Islands",
        "Mauritania",
        "Mauritius",
        "Mexico",
        "Micronesia",
        "Moldova",
        "Mongolia",
        "Montenegro",
        "Morocco",
        "Mozambique",
        "Myanmar",
        "Namibia",
        "Nauru",
        "Nepal",
        "Nicaragua",
        "Niger",
        "Nigeria",
        "North Macedonia",
        "Oman",
        "Pakistan",
        "Palau",
        "Panama",
        "Papua New Guinea",
        "Paraguay",
        "Peru",
        "Philippines",
        "Poland",
        "Qatar",
        "Romania",
        "Russia",
        "Rwanda",
        "Samoa",
        "São Tomé and Príncipe",
        "Saudi Arabia",
        "Senegal",
        "Serbia",
        "Seychelles",
        "Sierra Leone",
        "Solomon Islands",
        "Somalia",
        "South Africa",
        "South Sudan",
        "Sri Lanka",
        "St. Kitts and Nevis",
        "St. Lucia",
        "St. Vincent and the Grenadines",
        "Sudan",
        "Suriname",
        "Syria",
        "Tajikistan",
        "Tanzania",
        "Thailand",
        "Timor-Leste",
        "Togo",
        "Tonga",
        "Trinidad and Tobago",
        "Tunisia",
        "Türkiye",
        "Turkmenistan",
        "Tuvalu",
        "Uganda",
        "Ukraine",
        "United Arab Emirates",
        "Uruguay",
        "Uzbekistan",
        "Vanuatu",
        "Venezuela",
        "Vietnam",
        "West Bank and Gaza",
        "Yemen",
        "Zambia",
        "Zimbabwe",
    ]

    df = pd.DataFrame(countries, columns=["country"])
    df = add_iso_codes_column(df=df, id_column="country", id_type="regex")

    return df.iso_code.tolist()
