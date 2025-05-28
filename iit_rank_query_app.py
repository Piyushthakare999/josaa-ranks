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

rank = st.number_input("Enter your rank", min_value=1, value=1000)
year = st.selectbox("Select year", ["2022", "2023", "2024"])
category = st.selectbox("Select category", ["OPEN", "EWS", "OBC-NCL", "SC", "ST"])
gender = st.selectbox("Select gender", ["Gender-Neutral", "Female-only"])

with st.expander("ℹ️ Help"):
    st.markdown("""
    - **OR** = Opening Rank  
    - **CR** = Closing Rank  
    - **Status**:
        - *Aspirational* — CR is between (Rank - 300) and (Rank - 1)  
        - *Fitting* — OR ≤ Rank ≤ CR  
        - *Opening Down* — OR is greater than Rank but still close  
    - **Tip:** Double-click a column header in the table to sort by that column, and hover over the upper right edge to download the table or view it in fullscreen.
    """)


def create_status_column(df, rank, opening_down_limit=None):
    """Create status column with Aspirational, Fitting, Opening Down categories"""
    def get_status(row):
        or_val = row['OR']
        cr_val = row['CR']
        
        if (rank - 300) <= cr_val < rank:
            return 'Aspirational'
        elif or_val <= rank <= cr_val:
            return 'Fitting'
        elif or_val > rank:
            if opening_down_limit is None or or_val <= (rank + opening_down_limit):
                return 'Opening Down'
        return None
    
    return df.apply(get_status, axis=1)

def display_table_with_sections(df, rank, table_name, opening_down_limit=None):
    if df.empty:
        st.info(f"No programs available for {table_name}.")
        return
    
    df_with_status = df.copy()
    df_with_status['Status'] = create_status_column(df, rank, opening_down_limit)
    
    df_with_status = df_with_status.dropna(subset=['Status'])
    
    if df_with_status.empty:
        st.info(f"No programs available for {table_name} within the specified criteria.")
        return
    
    status_order = {'Fitting': 1, 'Aspirational': 2, 'Opening Down': 3}
    df_with_status['Status_Order'] = df_with_status['Status'].map(status_order)
    
    df_sorted = df_with_status.sort_values(['Status_Order', 'OR'])
    
    display_columns = ["Institute", "Program", "OR", "CR", "Status"]
    available_display_columns = [col for col in display_columns if col in df_sorted.columns]
    
    df_display = df_sorted[available_display_columns].reset_index(drop=True)
    
    st.markdown(f"**{len(df_display)} programs found for {table_name}:**")
    st.dataframe(df_display, hide_index=True)

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
        
        base_filter = (
            (df["Seat Type"].str.upper() == category.upper()) &
            (df["Gender"].str.contains(gender, case=False, na=False))
        )
        
        st.subheader("🎯 All Eligible Programs")
        st.caption("Aspirational: CR from rank-300 to rank-1 | Fitting: OR ≤ rank ≤ CR | Opening Down: OR from rank+1 to rank+500")
        
        table1_filter = base_filter & (
            ((df["CR"] >= (rank - 300)) & (df["CR"] < rank)) |
            ((df["OR"] <= rank) & (df["CR"] >= rank)) |
            ((df["OR"] > rank) & (df["OR"] <= (rank + 500)))
        )
        
        table1_df = df[table1_filter]
        
        st.markdown("---")
        st.subheader("⚡ Circuital Programmes")
        st.caption("Computer Science, Electrical, Electronics, Artificial Intelligence, and Mathematics programmes")
        st.caption("Aspirational: CR from rank-300 to rank-1 | Fitting: OR ≤ rank ≤ CR | Opening Down: All available OR > rank")
        
        circuital_keywords = ['Computer Science', 'Electrical', 'Electronics', 'Artificial', 'Mathematics']
        circuital_pattern = '|'.join(circuital_keywords)
        
        table2_filter = base_filter & (
            df["Program"].str.contains(circuital_pattern, case=False, na=False)
        ) & (
            ((df["CR"] >= (rank - 300)) & (df["CR"] < rank)) |
            ((df["OR"] <= rank) & (df["CR"] >= rank)) |
            (df["OR"] > rank)
        )
        
        table2_df = df[table2_filter]
        display_table_with_sections(table2_df, rank, "Circuital Programmes")
        
        st.markdown("---")
        st.subheader("🏛️ Old 7 IITs Branches")
        st.caption("Old IITs: Bombay, Delhi, Kharagpur, Madras, Kanpur, Roorkee, Guwahati")
        st.caption("Aspirational: OR from rank-300 to rank-1 | Fitting: OR ≤ rank ≤ CR | Opening Down: All available OR > rank")
        
        old_iits = ['Bombay', 'Delhi', 'Kharagpur', 'Madras', 'Kanpur', 'Roorkee', 'Guwahati']
        old_iits_pattern = '|'.join(old_iits)
        
        table3_filter = base_filter & (
            df["Institute"].str.contains(old_iits_pattern, case=False, na=False)
        ) & (
            ((df["OR"] >= (rank - 300)) & (df["OR"] < rank)) |
            ((df["OR"] <= rank) & (df["CR"] >= rank)) |
            (df["OR"] > rank)
        )
        
        table3_df = df[table3_filter]
        display_table_with_sections(table3_df, rank, "Old 7 IITs Branches")
            
    except Exception as e:
        st.error(f"Error processing data: {e}")
        st.write("Please check your CSV file format and column names.")
