import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

@st.cache_resource
def get_engine():
    return create_engine(os.environ["DATABASE_URL"])

@st.cache_data(ttl=60)
def query(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)
