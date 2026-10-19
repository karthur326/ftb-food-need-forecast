# Forecast output contract (DRAFT)

Agree this with the modeler early. The model writes it; Power BI only reads it.

Table: `FTB.GOLD.FORECAST_OUTPUT` (see `sql/10_forecast_output.sql`)

| Column | Type | Notes |
|---|---|---|
| `GEO_LEVEL` | string | `COUNTY`, `ZIP`, or `TRACT` |
| `GEO_ID` | string | FIPS (county/tract) or ZIP, always text, leading zeros kept |
| `MONTH` | date | First day of month |
| `MEASURE` | string | e.g. `FOOD_INSECURE_RATE`, `HOUSEHOLDS_IN_NEED`, `MEALS_NEEDED` |
| `SCENARIO` | string | `BASELINE` plus any others |
| `IS_FORECAST` | boolean | false for estimated actuals |
| `VALUE` | number | Point estimate |
| `LOWER` | number | Lower bound of interval |
| `UPPER` | number | Upper bound of interval |
| `MODEL_VERSION` | string | |
| `RUN_TS` | timestamp | When the model run was loaded |

Open questions for FTB and the modeler:
1. Geography (county, ZIP, tract)? Power BI map support differs a lot by level.
2. Horizon (months ahead)?
3. Which measure(s)?
4. Which scenarios, if any?
5. Interval definition (80%? 95%?).
