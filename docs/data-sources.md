# Data sources

Last audited: 2026-10-19 (schema, column and sample output pasted from Snowflake).

## Service area: 10 counties

Citrus, Hardee, Hernando, Highlands, Hillsborough, Manatee, Pasco, Pinellas, Polk, Sumter.
(Not Sarasota. The first mockup draft got this wrong and has been fixed.)

## Snowflake `FTB`

Schemas: `BRONZE` (not yet inspected), `SILVER`, `GOLD` (all owned by ACCOUNTADMIN).

### SILVER (dynamic tables, owner `CAPONETEAM`, change tracking on)

| Table | Rows | Notes |
|---|---|---|
| `CENSUS_TRACT` | 4,676 | More tracts than GOLD (2,161). Presumably wider region and/or filtered into GOLD |
| `COUNTY` | 50 | |
| `ZIP_CODE` | 1,027 | GOLD has 259 |

### GOLD (loaded by `FTB_LOADER_ROLE`, 2026-08-05)

| Table | Rows | Grain / columns of note |
|---|---|---|
| `ALICE_REPORT` | 10 | County. Households, poverty %, ALICE %, thresholds. **No year column** |
| `CHILD_FOOD_INSECURITY_MMG_SOUR` | 10 | County. Child population, child food insecurity rate, count, % under/over 185% FPL. **No year column** |
| `FTB_CENSUS_TRACT` | 2,161 | **Tract grain, single year (2023).** 1,169 real rows, one per tract (`GEOGRAPHY` = "Census Tract 4501.03", `COUNTY_SUBDIVISION` is actually the place name). The other **992 rows are blank** (NULL `YEAR`, NULL `GEOID`), likely empty spreadsheet rows. `COUSUBFP` is the Excel error `#REF!`. Columns: food bank IDs, overall food insecurity rate and count, range bucket, unemployment, poverty, median income, homeownership, disability, % Black, % Hispanic |
| `AGENCIES` | 293 | One row per agency: name, agency no, city, county, ZIP, tract GEOID, `MEALS_DISTRIBUTED`, `SUM_OF_GROSS_WEIGHT_LBS`. **Single total per agency, no date column** |
| `ZIP_COUNTY_TRACT_CITY_LOOKUP` | 119 | ZIP, county, tract GEOID, city. Only 119 rows for 259 ZIPs, so check coverage |
| `SCHOOL_PANTRIES` / `_ADDRESS` | 89 / 84 | Not yet inspected |
| `ZIP_CODES` | 259 | Not yet inspected |
| `DATA_SOURCES` | 16 | See below |

### `DATA_SOURCES`: previous cycle built a static need index

Weights: Food insecurity 40%, Financial insecurity 40%, Demographic indicators 20%.
Inputs come from Feeding America Map the Meal Gap (data from 2023), USDA Food Access Research Atlas
(recorded as data from 2009, check), and ACS tables S1401, B21001, B11009, S2801, S2701 (2024).
Everything is an annual snapshot. There is no monthly or weekly series.

## Findings

1. **No time series.** Everything in GOLD is a snapshot. `FTB_CENSUS_TRACT` holds only 2023, so there is
   no history to forecast from in GOLD. BRONZE has 1,400+ tables and is still unexplored.
   Map the Meal Gap is published annually, so a multi-year county series may be obtainable (verify).
2. **`MEALS_DISTRIBUTED` = lbs / 1.2** (198,260 lbs gives 165,217 meals), so the two columns are redundant.
3. **Agency totals are skewed by hubs.** Examples: Community Food Bank of Citrus 934,716 meals, Cutting Edge
   Ministries (Hardee) 659,831 vs typical pantries at 4,000 to 30,000. Hubs likely supply other agencies, so
   attributing meals to the hub's tract overstates local reach and double counts. Ask FTB.
4. **Dirty text:** city misspellings ("Iverness", "Ingles"). Use ZIP and GEOID for geography, never city.
5. **Types:** `GEOID`, `ZIP`, `ZIP_CODE` and FIPS are FLOAT. Cast to text (zero-padded) in SILVER/GOLD views.
   Florida values happen to be safe in float today, but this will bite on joins and in Power BI.
6. **Agency to tract join works:** agency `GEOID_AGENCES` is an 11-digit tract GEOID (e.g. 12017950500).

## Agency totals by county (period unknown)

| County | Agencies | Meals |
|---|---|---|
| Hillsborough | 110 | 20.9M |
| Pinellas | 39 | 14.2M |
| Polk | 46 | 9.1M |
| Pasco | 31 | 8.0M |
| Manatee | 26 | 4.4M |
| Highlands | 11 | 1.66M |
| Hernando | 9 | 1.45M |
| Citrus | 9 | 1.32M |
| Hardee | 6 | 1.13M |
| Sumter | 6 | 0.70M |

Largest agencies: St. Petersburg Free Clinic 4.57M, Hope Villages 3.42M, The Volunteer Way (Pasco) 2.18M.
Meals on Wheels East Pasco (0.9M) may be prepared meals, a different unit. Confirm.

## Real values for reference (county level)

Child food insecurity rate (MMG): Sumter 25.9%, Hardee 22.6%, Citrus 22.3%, Highlands 22.2%, Polk 20.3%,
Hernando 18.3%, Pinellas 17.6%, Hillsborough 17.2%, Manatee 16.7%, Pasco 16.4%.
ALICE plus poverty share of households is highest in Hernando (about 53%), Hardee, Highlands, Pasco.

## BRONZE: full ERP export already loaded (2026-08-06)

1,404 tables, 408 non-empty. Names are `Feeding Tampa Bay_<Table>`, with periods turned into underscores
(`Max_ Qty_`). A user name in the data points to **Microsoft Dynamics NAV (Navision)**, not NetSuite.
Confirm with FTB whether NAV is the legacy system and NetSuite the current one (check the last posting date).

Largest and most relevant tables:

| Table | Rows | Likely use |
|---|---|---|
| `Item Ledger Entry` | 5.0M | Every inventory movement, dated. Best candidate for distribution history |
| `Sales Shipment Header` / `Line` | 615K / 2.7M | Shipments to agencies (customers) |
| `Purch_ Rcpt_ Header` / `Line` | 562K / 2.1M | Food received (supply side) |
| `Value Entry`, `Warehouse Entry`, `Item Application Entry` | 5.0M to 5.6M | Valuation and warehouse movements |
| `Item`, `Item Unit of Measure` | 14K | Item master, units of measure (needed to convert to pounds) |
| `Parent Agency` | 584 | Agency master with address, ZIP, 501(c)(3) fields. **Contains contact names, phones and emails: keep out of the repo and out of reporting** |
| `UNC Donor ID`, `Food Drive Donor` | 7.9K, 617 | Donors |
| `MealConnect Order Line` | 1.3M | `Item No_`, `Quantity`, category (BP / FRESH), storage (DRY / REFRIG). No date or agency. `MealConnect Order Header` has only 5 rows, so lines can't be joined yet |

Gotchas for the pipeline:
- Dates are NUMBER microseconds since 1970. `-6847804800000000` is NAV's null date (1753-01-01).
- `timestamp` columns are BINARY row versions, not times. Useful for incremental loads only.
- Quote identifiers with spaces: `FTB.BRONZE."Feeding Tampa Bay_Item Ledger Entry"`.
- Parent Agency includes non-agency rows (ADMIN, DISASTER programs) and other food banks (e.g. Harry Chapin).

## NetSuite (status unknown)

Oracle ERP. Probably donations, inventory and shipments by agency. Open questions:
- What is tracked per agency and shipment? Dates? ZIP or address?
- Access method: existing export, SuiteAnalytics Connect (ODBC), SuiteQL REST, saved searches?
- Is `AGENCIES.MEALS_DISTRIBUTED` derived from NetSuite, and for what period?

## 211 (pending FTB data share agreement)

Helpline requests: leading indicator of need. FTB leads the agreement.
Open questions: location granularity (ZIP?), history depth, need categories, rate limits, aggregates only?

## Candidate public data (free)

| Source | Use | Grain |
|---|---|---|
| BLS LAUS | Unemployment | County, monthly |
| Florida DCF SNAP caseload | Benefit enrollment | County, monthly |
| Census ACS 5-year | Income, poverty, housing | Tract, annual |
| USDA Food Access Research Atlas | Low-access areas | Tract |
| BLS CPI food at home | Food price pressure | Regional, monthly |
| NOAA / FEMA storm events | Hurricane scenario | County |

## Caveat

Distribution counts reflect supply and agency locations, not true need. Prefer need indicators
(poverty, unemployment, 211 requests) as targets or features.
