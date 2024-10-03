# Trillions Tracker

The **Trillions Tracker** is a research project focused on tracking additional public finance available towards closing the estimated $3 trillion financing gap for development and climate needs in low and middle-income countries. This repository contains the data and code used to replicate the analysis as described in our [methodology document](https://observablehq.com/@one-campaign/trillions-tracker).

### TL;DR
The Trillions Tracker maps additional public finance available towards closing the $3 trillion gap identified by researchers for development and climate needs in low and middle income countries.

It uses 2019 as a baseline, pulling from the initial work, compared to resources available in 2022 (as well as some projected spending by MDBs and innovative finance). This work focuses on the US$2.5 trillion yearly official financing gap that must be closed by 2030, and does not track the $500 billion needed in private finance.

The Trillions Tracker considers:
- Domestic resource mobilisation (DRM) via _General Government Revenue_ data from the IMF, for developing and emerging economies, excluding China.
- Gross disbursements of Official Development Assistance, from all official donors who report data to the OECD DAC.
- Gross disbursements of non-concessional loans, from official bilateral and official multilateral sources (long-term, public and publicly guaranteed debt data from the World Bank International Debt Statistics)
- Channelled special drawing rights (or currency equivalents) that have been committed via the IMF’s  Poverty Reduction and Growth Trust (PRGT) and the Resilience and Sustainability Trust (RST)

All data is presented in 2019 US dollars, in constant prices and exchange rates. The decision of which data sources and specifications to choose came from a desire to match as closely as possible to the baseline funding presented in the research by Bhattacharya A et al (2022, p.46). 

## Replicating the analysis
To get started, you can clone this repository.

```bash
git clone https://github.com/yourusername/trillions-tracker.git
cd trillions-tracker
```

You will need to install the dependencies using poetry.

```bash
pip install poetry
poetry install
```
The [scripts](./scripts) folder contains Python scripts for extracting and analysing DAC data (ODA, OOFs), Debt data from the IDS, and DRM data from the World Economic Outlook.


## Using the outputs
The [output](./output) folder contains the different files we use in our data visualisations. For now, it does not contain raw data or other outputs.


## Getting additional data
If you would like us to add additional data exports on any of the sources covered by the Trillions Tracker, please [create an issue](https://github.com/ONEcampaign/trillions_tracker/issues) with your request.
