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
    

    circuital_keywords = ['Computer Science', 'Electrical', 'Electronics', 'Artificial', 'Mathematics']
    circuital_pattern = '|'.join(circuital_keywords)
    
    circuital = df[
        (df["Seat Type"].str.upper() == category.upper()) &
        (df["Gender"].str.contains(gender, case=False)) &
        (df["OR"] > rank) &
        (df["Program"].str.contains(circuital_pattern, case=False, na=False))
    ]
    
    if filtered.empty:
        st.warning("No eligible programs found for the given criteria.")
    else:
        st.success(f"Found {len(filtered)} eligible programs:")
        st.dataframe(filtered[["Institute", "Program", "OR", "CR"]].sort_values("OR"))
    

    st.markdown("---")
    if circuital.empty:
        st.info("No circuital programmes available (programs with OR below your rank).")
    else:
        st.subheader("Circuital Programmes (Below Rank) Available")
        st.markdown(f"**{len(circuital)} Circuital programmes with Opening Rank below your rank of {rank}:**")
        st.caption("Showing only: Computer Science, Electrical, Electronics, Artificial Intelligence, and Mathematics programmes")
        st.dataframe(circuital[["Institute", "Program", "OR", "CR"]].sort_values("OR"))

st.markdown("""<hr style="margin-top: 2em;">""", unsafe_allow_html=True)
st.markdown("<center><sub>Created by Musaib Bin Bashir</sub></center>", unsafe_allow_html=True)
