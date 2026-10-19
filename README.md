# FTB Food Need Forecast Map

Volunteer project (Capital One pro bono cycle) for Feeding Tampa Bay: a Power BI
dashboard that shows projected food need across the Tampa Bay area and surrounding
counties.

## Status

Early. Data audit and mockup stage. Nothing here is production.

## Layout

| Path | What |
|---|---|
| `mockup/` | Clickable HTML mockup with **fake data**, used to gather requirements from FTB |
| `docs/data-sources.md` | What we know (and don't) about each data source |
| `docs/forecast-output-contract.md` | Proposed table the model writes and Power BI reads |
| `sql/` | Snowflake exploration queries and DDL for the forecast output and reporting role |
| `pipelines/` | Python ingestion stubs (NetSuite, 211, public data) |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in
```

## Data handling

This repo must not contain real FTB data, client-level data, or credentials.
`data/`, `*.csv`, `*.parquet`, and `.env` are git-ignored. The mockup uses invented numbers only.
