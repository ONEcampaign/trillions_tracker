# Data from the OECD DAC

This folder contains tools to extract data from the OECD DAC databases. 

Note that certain settings that affect how we get and process data are included in the [config.py](../config.py) file. That includes settings like the list of bilateral donors, the list of developing countries recipients (for non CRS data), and whether to exclude China and IDRC.

## [ODA.py](./oda.py)

This script contains tools to get ODA specifically. The `get_oda_data` function wraps around `ODAData` to handle getting a specific indicator from the list of bilateral donors.

The data can be provided at different levels of aggregation. By default it returns a single value per year, but it can return data disaggregated by donor, and for some indicators, by recipient.

The list of available indicators can be found in the [tools.py](./tools.py) file.


## [tools.py](./tools.py)

The tools script contains a series of helpers to process the OECD DAC data.

It also includes a function to get and process data from the CRS (access, filter, group, transform to constant).

The `INDICATORS` dictionary maps indicator names to more readable names, and provides convenient access to the indicators that can be used for this project.

The `REFUGEE_MODS` list contains the modalities that are considered to be "In-donor refugee costs" in the OECD DAC data. The list is **only** used to exlude these flows from CRS data.

Other tools include:
- A function to convert data to constant USD, using DAC deflators
- A function to filter to keep only ODA data
- A function to group data by all columns excluding 'donors'
- A function to group data by all columns excluding 'recipients'
- A function to add bilateral donor names
- A function to filter recipients to include only countries and regions (no unspecified data)

## [bilateral_oda.py](./bilateral_oda.py)

This script gets bilateral data for a specific indicator through `bilateral_oda` and calculates a few key statistics for this research project.