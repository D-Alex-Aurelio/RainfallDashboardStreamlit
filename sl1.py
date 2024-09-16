import streamlit as st

with st.sidebar:
    st.write("This is a sidebar")
    st.write("I am in a sidebar")
    uploaded_file = st.file_uploader("Choose a CSV file")

st.write("I am not in a sidebar")

tab1, tab2, tab3 = st.tabs(["Yearly Analysis", "Monthly Analysis", "Daily Analysis"])

with tab1:
    st.header("This is for the Yearly Analysis of Rainfall Data")

with tab2:
    st.header("This is for the Monthly Analysis of Rainfall Data")

with tab3:
    st.header("This is for the Daily Analysis of Rainfall Data")