# Data sources

## Snowflake: `FTB.GOLD` (known, as of 2026-08-05 load)

| Table | Rows | Notes |
|---|---|---|
| `AGENCIES` | 293 | Partner agencies. Need: lat/long or address? ZIP? |
| `ALICE_REPORT` | 10 | Likely county-level, annual. Confirm grain |
| `CHILD_FOOD_INSECURITY_MMG_SOUR` | 10 | Map the Meal Gap, likely county-level. Confirm grain and years |
| `DATA_SOURCES` | 16 | May document lineage. Read first |
| `FTB_CENSUS_TRACK` | 2,161 | Census tracts in service area |
| `SCHOOL_PANTRIES` | 89 | |
| `SCHOOL_PANTRIES_ADDRESS` | 84 | 5 fewer than pantries. Check join |
| `ZIP_CODES` | 259 | |
| `ZIP_COUNTY_TRACT_CITY_LOOKUP` | 119 | Crosswalk. Only 119 rows vs 2,161 tracts, so check coverage |

Observation: no time-series fact table (pounds, households served, visits by agency/ZIP/month) in GOLD.
Check other schemas (`SHOW SCHEMAS IN DATABASE FTB`).

## NetSuite (not yet accessed)

Oracle ERP. Probably donations, inventory, and shipments by agency. Open questions:
- What is tracked at agency/shipment level? Do records have ZIP or address?
- Access method: existing export, SuiteAnalytics Connect (ODBC), SuiteQL over REST, saved searches?
- Is any of it already in Snowflake (other schemas)?

## 211 (pending FTB data share agreement)

Helpline requests: leading indicator of need. FTB is leading the agreement and will share API details.
Open questions: location granularity (ZIP?), history depth, need categories, rate limits, aggregates only?

## Candidate public data (free)

| Source | Use | Grain |
|---|---|---|
| Census ACS 5-year | Income, poverty, housing cost, demographics | Tract |
| BLS LAUS | Unemployment | County, monthly |
| Florida DCF SNAP caseload | Benefit enrollment | County, monthly |
| USDA Food Access Research Atlas | Low-access areas | Tract |
| BLS CPI (food at home) | Food price pressure | Regional, monthly |
| NOAA / FEMA storm events | Hurricane scenario | County |
| Feeding America Map the Meal Gap | Already loaded | County |

## Caveat

Distribution/served counts reflect supply and agency locations, not true need. Prefer need
indicators (poverty, unemployment, 211 requests) as targets or features where possible.
