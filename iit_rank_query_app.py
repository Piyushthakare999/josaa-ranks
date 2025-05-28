import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df_2023 = pd.read_csv("ranks2023.csv")
    df_2024 = pd.read_csv("ranks2024.csv")
    return df_2023, df_2024

df_2023, df_2024 = load_data()

st.title(" IIT College & Branch Finder")
st.markdown("Enter your rank to see eligible colleges and programs based on category and gender.")


rank = st.number_input("Enter your rank", min_value=1)
year = st.selectbox("Select year", ["2023", "2024"])
category = st.selectbox("Select category", ["OPEN", "EWS", "OBC-NCL", "SC", "ST"])
gender = st.selectbox("Select gender", ["Gender-Neutral", "Female-only"])

if st.button("Find Eligible Programs"):
    df = df_2023 if year == "2023" else df_2024
    filtered = df[
        (df["Seat Type"].str.upper() == category.upper()) &
        (df["Gender"].str.contains(gender, case=False)) &
        (df["OR"] <= rank) & (df["CR"] >= rank)
    ]
    if filtered.empty:
        st.warning("No eligible programs found for the given criteria.")
    else:
        st.success(f"Found {len(filtered)} eligible programs:")
        st.dataframe(filtered[["Institute", "Program", "OR", "CR"]].sort_values("OR"))

