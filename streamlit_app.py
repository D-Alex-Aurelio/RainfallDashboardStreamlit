from operator import index

import pandas as pd
import streamlit as st

df = pd.read_csv("data/default data.csv")

with st.sidebar:
    uploaded_file = st.file_uploader("Choose a CSV file")

st.title("Rainfall Analysis Dashboard")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

df = pd.DataFrame(
    index = pd.to_datetime(df[["YEAR","MONTH","DAY"]]),
    data={
        "RAINFALL": [x if x >= 0 else 0 for x in df["RAINFALL"].values]
    }
)
df_year = df.groupby(by=df.index.year).sum()/1000
df_month = pd.pivot_table(df,
                          values="RAINFALL",
                          index=[df.index.month],
                          columns=[df.index.year],
                          aggfunc="sum")

tab1, tab2, tab3 = st.tabs(["Yearly Analysis", "Monthly Analysis", "Daily Analysis"])

with tab1:
    st.header("This is for the Yearly Analysis of Rainfall Data")
    st.write(df_year)

with tab2:
    st.header("This is for the Monthly Analysis of Rainfall Data")
    st.write(df_month)

with tab3:
    st.header("This is for the Daily Analysis of Rainfall Data")
    st.write(df)
