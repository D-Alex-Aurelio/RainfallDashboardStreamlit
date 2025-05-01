from operator import index

from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

import pandas as pd
import streamlit as st
import plotly.express as px

def filter_dataframe(df_f: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df_f (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df_f

    df_f = df_f.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df_f.columns:
        if is_object_dtype(df_f[col]):
            try:
                df_f[col] = pd.to_datetime(df_f[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df_f[col]):
            df_f[col] = df_f[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df_f.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical

            if isinstance(df_f[column],pd.CategoricalDtype) or df_f[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df_f[column].unique(),
                    default=list(df_f[column].unique()),
                )
                df_f = df_f[df_f[column].isin(user_cat_input)]
            elif is_numeric_dtype(df_f[column]):
                _min = float(df_f[column].min())
                _max = float(df_f[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df_f = df_f[df_f[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df_f[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df_f[column].min(),
                        df_f[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df_f = df_f.loc[df_f[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df_f = df_f[df_f[column].astype(str).str.contains(user_text_input)]

    return df_f

df = pd.read_csv("data/default data.csv")

with st.sidebar:
    uploaded_file = st.file_uploader("Choose a CSV file")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write(df.head())
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
    st.divider()
    st.header("Assumptions")
    st.write("Missing data is equivalent to zero.")

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


# dashboard layout
st.title("Rainfall Analysis Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["Raw Data","Yearly Analysis", "Monthly Analysis", "Daily Analysis"])

with tab1:
    st.header("Raw Data")
    st.dataframe(filter_dataframe(df),use_container_width=True)

with tab2:
    st.header("Yearly Rainfall Trend and Statistics")
    yearly_color = st.color_picker("Pick a color:","#2892A2")
    st.write("The color is", yearly_color)
    yearly_plot_1 = px.bar(df_year,
                           x=df_year.index,
                           y="RAINFALL")
    yearly_plot_1.update_layout(xaxis_title="Year",
                                yaxis_title="Rainfall, meters")
    yearly_plot_1.update_traces(hovertemplate="Year: %{x} <br>Rainfall: %{y} meters",
                                marker_color=yearly_color)

    st.plotly_chart(yearly_plot_1)
    st.write(df_year.describe())

with tab3:
    st.header("Monthly Rainfall Trend")
    monthly_color_option = st.selectbox("Color Scheme:",
                          ("Blues","Reds","Greens","Oranges", "Greys"))
    st.write("You selected:", monthly_color_option)

    monthly_plot_1 = px.imshow(df_month,
                               color_continuous_scale=monthly_color_option,
                               labels=dict(x="Year",y="Month",color="Rainfall, cm"),
                               y=["Jan","Feb","Mar","Apr","May","June",
                                  "July","Aug","Sept","Oct","Nov","Dec"])
    st.plotly_chart(monthly_plot_1)

    st.header("Monthly Rainfall Statistics")

    monthly_color = st.color_picker("Pick a color:","#9787d4")
    st.write("The color is", monthly_color)

    monthly_plot_2 = px.box(df_month).update_layout(xaxis_title="Year",
                                                    yaxis_title="Rainfall, cm")
    monthly_plot_2.update_traces(marker_color=monthly_color)

    st.plotly_chart(monthly_plot_2)
    st.write(df_month.describe())

with tab4:
    st.header("Daily Rainfall Trend")

    daily_color = st.color_picker("Pick a color:", "#D487D3")
    st.write("The color is", daily_color)

    daily_plot_1 = px.line(df,
                           y="RAINFALL")
    daily_plot_1.update_layout(xaxis_title="",
                               yaxis_title="Rainfall, mm")
    daily_plot_1.update_traces(hovertemplate="Date: %{x} <br>Rainfall: %{y} mm",
                               line_color = daily_color)
    st.plotly_chart(daily_plot_1)

    st.header("Daily Rainfall Statistics")
    st.write(df_rf["RAINFALL"].describe())
    daily_plot_2 = px.line(df_rf,
                           x="RAINFALL",
                           y="POSITION")
    daily_plot_2.update_layout(xaxis_title="Rainfall, mm",
                               yaxis_title="Position")
    daily_plot_2.update_traces(hovertemplate="Position: %{y:.3f} <br>Rainfall, mm: %{x}",
                               line_color = daily_color)

    st.plotly_chart(daily_plot_2)
    rf_percs = [70,75,80,85,90,95,99]
    rf_vals = []
    for rf_perc in rf_percs:
        rf_vals.append(df_rf[df_rf["POSITION"]>rf_perc/100]["RAINFALL"].iloc[0])
    df_perc = pd.DataFrame({"PERCENTILE": rf_percs,"RAINFALL": rf_vals})
    st.write(df_perc)

