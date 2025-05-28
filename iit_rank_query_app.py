import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    try:
        df_2022 = pd.read_csv("ranks2022.csv")
        df_2023 = pd.read_csv("ranks2023.csv")
        df_2024 = pd.read_csv("ranks2024.csv")
        return df_2022, df_2023, df_2024
    except FileNotFoundError as e:
        st.error(f"CSV file not found: {e}")
        return None, None, None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

df_2022, df_2023, df_2024 = load_data()

if df_2022 is None or df_2023 is None or df_2024 is None:
    st.stop()

st.markdown("<h1 style='text-align: center;'>🎓 IIT College & Branch Finder</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Enter your rank to see eligible colleges and programs based on category and gender.</p>", unsafe_allow_html=True)
st.markdown("""<hr style="margin-top: 2em;">""", unsafe_allow_html=True)
st.markdown("<center><sub>Created by Musaib Bin Bashir</sub></center>", unsafe_allow_html=True)

rank = st.number_input("Enter your rank", min_value=1, value=1)
year = st.selectbox("Select year", ["2022", "2023", "2024"])
category = st.selectbox("Select category", ["OPEN", "EWS", "OBC-NCL", "SC", "ST"])
gender = st.selectbox("Select gender", ["Gender-Neutral", "Female-only"])

if st.button("Find Eligible Programs"):
    if year == "2022":
        df = df_2022
    elif year == "2023":
        df = df_2023
    else:
        df = df_2024
    
    try:
        required_columns = ["Seat Type", "Gender", "OR", "CR", "Institute", "Program"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing columns in CSV: {missing_columns}")
            st.write("Available columns:", df.columns.tolist())
            st.stop()
        
        filtered = df[
            (df["Seat Type"].str.upper() == category.upper()) &
            (df["Gender"].str.contains(gender, case=False, na=False)) &
            (df["OR"] <= rank) & 
            (df["CR"] >= rank)
        ]
        
        circuital_keywords = ['Computer Science', 'Electrical', 'Electronics', 'Artificial', 'Mathematics']
        circuital_pattern = '|'.join(circuital_keywords)
        
        circuital = df[
            (df["Seat Type"].str.upper() == category.upper()) &
            (df["Gender"].str.contains(gender, case=False, na=False)) &
            (df["Program"].str.contains(circuital_pattern, case=False, na=False)) &
            ((df["OR"] > rank) | ((df["OR"] <= rank) & (df["CR"] >= rank)))
        ]
        
        old_iits = ['Bombay', 'Delhi', 'Kharagpur', 'Madras', 'Kanpur', 'Roorkee', 'Guwahati']
        old_iits_pattern = '|'.join(old_iits)
        
        old_iits_branches = df[
            (df["Seat Type"].str.upper() == category.upper()) &
            (df["Gender"].str.contains(gender, case=False, na=False)) &
            (df["Institute"].str.contains(old_iits_pattern, case=False, na=False)) &
            ((df["OR"] > rank) | ((df["OR"] <= rank) & (df["CR"] >= rank)))
        ]
        
        if filtered.empty:
            st.warning("No eligible programs found for the given criteria.")
        else:
            st.success(f"Found {len(filtered)} eligible programs with OR ≤ {rank} ≤ CR:")
            display_columns = ["Institute", "Program", "OR", "CR"]
            available_display_columns = [col for col in display_columns if col in df.columns]
            st.dataframe(filtered[available_display_columns].sort_values("OR"))
        

        st.markdown("---")
        if circuital.empty:
            st.info("No circuital programmes available.")
        else:
            st.subheader("Circuital Programmes Available")
            st.markdown(f"**{len(circuital)} Circuital programmes (either eligible or with higher opening ranks):**")
            st.caption("Showing: Computer Science, Electrical, Electronics, Artificial Intelligence, and Mathematics programmes")
            st.caption("Includes both fitting programs (where you can get admission) and opening down programs (easier to get)")
            display_columns = ["Institute", "Program", "OR", "CR"]
            available_display_columns = [col for col in display_columns if col in df.columns]
            
            circuital_display = circuital[available_display_columns].copy()
            circuital_display['Status'] = circuital_display.apply(
                lambda row: 'Fitting' if (row['OR'] <= rank <= row['CR']) else 'Opening Down', axis=1
            )
            st.dataframe(circuital_display.sort_values("OR"))
        
        st.markdown("---")
        if old_iits_branches.empty:
            st.info("No branches available at Old 7 IITs.")
        else:
            st.subheader("Branches Available at Old 7 IITs")
            st.markdown(f"**{len(old_iits_branches)} programmes at old 7 IITs (either eligible or with higher opening ranks):**")
            st.caption("Old IITs: Bombay, Delhi, Kharagpur, Madras, Kanpur, Roorkee, Guwahati")
            st.caption("Includes both fitting programs (where you can get admission) and opening down programs (easier to get)")
            display_columns = ["Institute", "Program", "OR", "CR"]
            available_display_columns = [col for col in display_columns if col in df.columns]
            
            old_iits_display = old_iits_branches[available_display_columns].copy()
            old_iits_display['Status'] = old_iits_display.apply(
                lambda row: 'Fitting' if (row['OR'] <= rank <= row['CR']) else 'Opening Down', axis=1
            )
            st.dataframe(old_iits_display.sort_values("OR"))
            
    except Exception as e:
        st.error(f"Error processing data: {e}")
        st.write("Please check your CSV file format and column names.")
