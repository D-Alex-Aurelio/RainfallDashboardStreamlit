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

df.columns = ["YEAR","MONTH","DAY","RAINFALL"]
df = pd.DataFrame(
    index = pd.to_datetime(df[["YEAR","MONTH","DAY"]]),
    data={
        "RAINFALL": [x if x >= 0 else 0 for x in df["RAINFALL"].values]
    }
)
# convert mm to m for yearly analysis
df_year = df.groupby(by=df.index.year).sum()/1000


# convert mm to cm for monthly analysis
df_month = pd.DataFrame(df)
df_month["RAINFALL"] = df_month["RAINFALL"]/10
df_month = pd.pivot_table(df_month,
                          values="RAINFALL",
                          index=[df_month.index.month],
                          columns=[df_month.index.year],
                          aggfunc="sum")

# adding position to daily rainfall
df_rf = pd.DataFrame({"RAINFALL":df["RAINFALL"].values})
df_rf = df_rf.sort_values(by="RAINFALL", ignore_index=True)
df_rf["POSITION"] = (list(range(1,df_rf.count().iloc[0]+1,1)))/(df_rf.count().iloc[0]+1)


tab1, tab2, tab3 = st.tabs(["Yearly Analysis", "Monthly Analysis", "Daily Analysis"])

with tab1:
    st.header("Yearly Rainfall Trend and Statistics")
    yearly_plot_1 = px.bar(df_year,
                           x=df_year.index,
                           y="RAINFALL")
    yearly_plot_1.update_layout(xaxis_title="Year",
                                yaxis_title="Rainfall, meters")
    yearly_plot_1.update_traces(hovertemplate="Year: %{x} <br>Rainfall: %{y} meters")

    st.plotly_chart(yearly_plot_1)
    st.write(df_year.describe())

with tab2:
    st.header("Monthly Rainfall Trend")
    monthly_plot_1 = px.imshow(df_month,
                               color_continuous_scale="Blues",
                               labels=dict(x="Year",y="Month",color="Rainfall, cm"),
                               y=["Jan","Feb","Mar","Apr","May","June",
                                  "July","Aug","Sept","Oct","Nov","Dec"])
    st.plotly_chart(monthly_plot_1)

    st.header("Monthly Rainfall Statistics")
    monthly_plot_2 = px.box(df_month).update_layout(xaxis_title="Year",
                                                    yaxis_title="Rainfall, cm")
    st.plotly_chart(monthly_plot_2)
    st.write(df_month.describe())

with tab3:
    st.header("Daily Rainfall Trend")
    daily_plot_1 = px.line(df,
                           y="RAINFALL")
    daily_plot_1.update_layout(xaxis_title="",
                               yaxis_title="Rainfall, mm")
    daily_plot_1.update_traces(hovertemplate="Date: %{x} <br>Rainfall: %{y} mm")
    st.plotly_chart(daily_plot_1)

    st.header("Daily Rainfall Statistics")
    st.write(df_rf["RAINFALL"].describe())
    daily_plot_2 = px.line(df_rf,
                           x="RAINFALL",
                           y="POSITION")
    daily_plot_2.update_layout(xaxis_title="Rainfall, mm",
                               yaxis_title="Position")
    daily_plot_2.update_traces(hovertemplate="Position: %{y:.3f} <br>Rainfall, mm: %{x}")
    st.plotly_chart(daily_plot_2)
    rf_percs = [70,75,80,85,90,95,99]
    rf_vals = []
    for rf_perc in rf_percs:
        rf_vals.append(df_rf[df_rf["POSITION"]>rf_perc/100]["RAINFALL"].iloc[0])
    df_perc = pd.DataFrame({"PERCENTILE": rf_percs,"RAINFALL": rf_vals})
    st.write(df_perc)

