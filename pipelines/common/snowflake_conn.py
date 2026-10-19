"""Shared Snowflake connection, configured from environment (.env)."""
import os

import snowflake.connector
from dotenv import load_dotenv


def get_connection() -> snowflake.connector.SnowflakeConnection:
    load_dotenv()
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        authenticator=os.environ.get("SNOWFLAKE_AUTHENTICATOR", "externalbrowser"),
        role=os.environ.get("SNOWFLAKE_ROLE"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "FTB"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "GOLD"),
    )
