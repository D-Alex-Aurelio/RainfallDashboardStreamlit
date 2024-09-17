from operator import index

import pandas as pd
import streamlit as st
import plotly.express as px

df = pd.read_csv("data/default data.csv")

with st.sidebar:
    uploaded_file = st.file_uploader("Choose a CSV file")
    st.divider()
    st.header("File Preparation")
    st.write("1. Data must be in the following format:")
    df_example = pd.DataFrame({
        "YEAR":["XXXX"],
        "MONTH":["XX"],
        "DAY":["XX"],
        "RAINFALL":["XX.XX"]
    })
    st.write(df_example)
    st.write("2. Rainfall must be a number")

st.title("Rainfall Analysis Dashboard")
st.header("Assumptions")
st.write("Missing data is equivalent to zero.")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

df = pd.DataFrame(
    index = pd.to_datetime(df[["YEAR","MONTH","DAY"]]),
    data={
        "RAINFALL": [x if x >= 0 else 0 for x in df["RAINFALL"].values]
    }
)
# convert mm to m for yearly analysis
df_year = df.groupby(by=df.index.year).sum()/1000


# convert mm to cm for monthly analysis
df_month = df
df_month['RAINFALL'] = df_month['RAINFALL']/10
df_month = pd.pivot_table(df_month,
                          values="RAINFALL",
                          index=[df.index.month],
                          columns=[df.index.year],
                          aggfunc="sum")



tab1, tab2, tab3 = st.tabs(["Yearly Analysis", "Monthly Analysis", "Daily Analysis"])

with tab1:
    st.header("Yearly Rainfall Trend and Statistics")
    yearly_plot_1 = px.bar(df_year)
    st.plotly_chart(yearly_plot_1)
    st.write(f"Max: {df_year.max().iloc[0]} meters")
    st.write(f"Min: {df_year.min().iloc[0]} meters")
    st.write(f"Median: {df_year.median().iloc[0]} meters")

with tab2:
    st.header("Monthly Rainfall Trend")
    monthly_plot_1 = px.imshow(df_month, color_continuous_scale="Blues")
    st.plotly_chart(monthly_plot_1)
    st.header("Monthly Rainfall Statistics")
    monthly_plot_2 = px.box(df_month)
    st.plotly_chart(monthly_plot_2)

with tab3:
    st.header("This is for the Daily Analysis of Rainfall Data")
    st.write(df)
