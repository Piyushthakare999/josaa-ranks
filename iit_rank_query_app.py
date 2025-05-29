import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def load_data():
    try:
        df_iit_2022 = pd.read_csv("data/ranks2022.csv")
        df_iit_2023 = pd.read_csv("data/ranks2023.csv")
        df_iit_2024 = pd.read_csv("data/ranks2024.csv")
        
        df_nit_2022 = pd.read_csv("data/nits2022.csv")
        df_nit_2023 = pd.read_csv("data/nits2023.csv")
        df_nit_2024 = pd.read_csv("data/nits2024.csv")
        
        df_iiit_2022 = pd.read_csv("data/IIITs2022.csv")
        df_iiit_2023 = pd.read_csv("data/IIITs2023.csv")
        df_iiit_2024 = pd.read_csv("data/IIITs2024.csv")
        
        df_gfti_2022 = pd.read_csv("data/GFTIs2022.csv")
        df_gfti_2023 = pd.read_csv("data/GFTIs2023.csv")
        df_gfti_2024 = pd.read_csv("data/GFTIs2024.csv")
        
        return {
            'IIT': {2022: df_iit_2022, 2023: df_iit_2023, 2024: df_iit_2024},
            'NIT': {2022: df_nit_2022, 2023: df_nit_2023, 2024: df_nit_2024},
            'IIIT': {2022: df_iiit_2022, 2023: df_iiit_2023, 2024: df_iiit_2024},
            'GFTI': {2022: df_gfti_2022, 2023: df_gfti_2023, 2024: df_gfti_2024}
        }
    except FileNotFoundError as e:
        st.error(f"CSV file not found: {e}")
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def clean_rank_data(df):
    if df is None or df.empty:
        return df
    

    df_clean = df.copy()
    

    for col in ['OR', 'CR']:
        if col in df_clean.columns:

            df_clean[col] = df_clean[col].astype(str)
            df_clean[col] = df_clean[col].str.replace(r'[^\d.]', '', regex=True)
            df_clean[col] = df_clean[col].replace('', np.nan)
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    

    if 'OR' in df_clean.columns and 'CR' in df_clean.columns:
        df_clean = df_clean.dropna(subset=['OR', 'CR'])
    
    return df_clean

data_dict = load_data()

if data_dict is None:
    st.stop()


for inst_type in data_dict:
    for year in data_dict[inst_type]:
        data_dict[inst_type][year] = clean_rank_data(data_dict[inst_type][year])

st.markdown("<h1 style='text-align: center;'>🎓 JOSAA College & Branch Finder</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Find eligible colleges and programs across IITs, NITs, IIITs, and GFTIs based on your JEE rank, category, and gender.</p>", unsafe_allow_html=True)
st.markdown("""<hr style="margin-top: 2em;">""", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Created by Musaib Bin Bashir.</p>", unsafe_allow_html=True)

exam_type = st.selectbox("Select exam", ["JEE Advanced", "JEE Mains"])
rank = st.number_input(f"Enter your {exam_type} rank (category rank, if applicable)", min_value=1, value=1000)
year = st.selectbox("Select year", [2022, 2023, 2024])

if exam_type == "JEE Advanced":
    institute_type = "IITs"
    st.info("🎯 JEE Advanced: Showing IIT programs only")
else:
    institute_type = st.selectbox("Select institute type", ["ALL", "NITs", "IIITs", "GFTIs"])

category = st.selectbox("Select category", ["OPEN", "EWS", "OBC-NCL", "SC", "ST", "PwD"])
gender = st.selectbox("Select gender", ["Gender-Neutral", "Female-only"])

with st.expander("ℹ️ Help"):
    st.markdown("""
    - **OR** = Opening Rank  
    - **CR** = Closing Rank  
    - **Status**:
        - *Aspirational* — CR is between (Rank - 300) and (Rank - 1)  
        - *Fitting* — OR ≤ Rank ≤ CR  
        - *Opening Down* — OR is greater than Rank but still close  
    - **Exams**:
        - *JEE Advanced* — For IIT admissions (shows IIT programs only)
        - *JEE Mains* — For NIT, IIIT, GFTI admissions
    - **Institute Types** (for JEE Mains):
        - *NITs* — National Institutes of Technology  
        - *IIITs* — Indian Institutes of Information Technology
        - *GFTIs* — Government Funded Technical Institutions
        - *ALL* — Shows combined results from all institute types
    - **Categories**:
        - *PwD* — Persons with Disabilities (includes OPEN(PwD), SC(PwD), OBC-NCL(PwD), etc.)
        - Other categories work as usual
    - **Tips**: 
        - Double-click a column header in the table to sort by that column
        - Hover over the upper right edge to download the table or view it in fullscreen.
    """)
    
    st.markdown("""
    - **Quota Types** (for NITs, IIITs, GFTIs):
        - *OS* = Other State quota
        - *HS* = Home State quota
        - *AI* = All India Quota
        - Results will show both OS and HS quotas in the Quota column where applicable
        - *NOTE*= For programs with Reservations/Categories, the OR AND CR shown correspond to Category Rank
    """)

def create_status_column(df, rank, opening_down_limit=None):
    def get_status(row):
        try:
            or_val = float(row['OR'])
            cr_val = float(row['CR'])
            
            if (rank - 300) <= cr_val < rank:
                return 'Aspirational'
            elif or_val <= rank <= cr_val:
                return 'Fitting'
            elif or_val > rank:
                if opening_down_limit is None or or_val <= (rank + opening_down_limit):
                    return 'Opening Down'
        except (ValueError, TypeError):

            pass
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
    if "Quota" in df_sorted.columns:
        display_columns = ["Institute", "Program", "Quota", "OR", "CR", "Status"]
    if "Institute_Type" in df_sorted.columns:
        display_columns = ["Institute_Type"] + display_columns
    
    available_display_columns = [col for col in display_columns if col in df_sorted.columns]
    
    df_display = df_sorted[available_display_columns].reset_index(drop=True)
    
    st.markdown(f"**{len(df_display)} programs found for {table_name}:**")
    st.dataframe(df_display, hide_index=True)

def get_combined_dataframe(year, institute_types, category, gender):
    combined_df = pd.DataFrame()
    
    for inst_type in institute_types:
        if inst_type in data_dict and year in data_dict[inst_type]:
            df = data_dict[inst_type][year].copy()
            
            if df is None or df.empty:
                continue
                
            df['Institute_Type'] = inst_type
            
            required_base_columns = ["Seat Type", "Gender", "OR", "CR", "Institute", "Program"]
            if not all(col in df.columns for col in required_base_columns):
                st.warning(f"Skipping {inst_type} {year} data due to missing columns")
                continue
            
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    return combined_df

def safe_numeric_filter(df, column, operator, value):
    try:
        if operator == '>=':
            return pd.to_numeric(df[column], errors='coerce') >= value
        elif operator == '<=':
            return pd.to_numeric(df[column], errors='coerce') <= value
        elif operator == '>':
            return pd.to_numeric(df[column], errors='coerce') > value
        elif operator == '<':
            return pd.to_numeric(df[column], errors='coerce') < value
    except:
        return pd.Series([False] * len(df))

def create_category_filter(df, category):
    """Create appropriate filter for category including PwD support"""
    if category == "PwD":
        return df["Seat Type"].str.contains(r'\(PwD\)', case=False, na=False)
    else:
        return df["Seat Type"].str.upper() == category.upper()

if st.button("Find Eligible Programs"):
    try:
        if exam_type == "JEE Advanced":
            institute_types = ["IIT"]
            display_name = "IITs"
        elif institute_type == "ALL":
            institute_types = ["NIT", "IIIT", "GFTI"] 
            display_name = "All Engineering Colleges (NITs, IIITs, GFTIs)"
        else:
            institute_types = [institute_type.rstrip('s').upper()]  
            display_name = institute_type
        
        if exam_type == "JEE Advanced":
            df = get_combined_dataframe(year, institute_types, category, gender)
        elif exam_type == "JEE Mains" and institute_type == "ALL":
            df = get_combined_dataframe(year, institute_types, category, gender)
        else:
            inst_key = institute_types[0]
            if inst_key in data_dict and year in data_dict[inst_key]:
                df = data_dict[inst_key][year].copy()
            else:
                st.error(f"Data not available for {institute_type} {year}")
                st.stop()
        
        if df.empty:
            st.error(f"No data available for the selected criteria")
            st.stop()
        
        required_columns = ["Seat Type", "Gender", "OR", "CR", "Institute", "Program"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing columns in data: {missing_columns}")
            st.write("Available columns:", df.columns.tolist())
            st.stop()
        
        base_filter = (
            create_category_filter(df, category) &
            (df["Gender"].str.contains(gender, case=False, na=False))
        )
        
        st.subheader("🎯 All Recommended Programs")
        st.caption("Note: Recommended Programs include those program which satisfy OR< your rank < CR")
        st.caption("Aspirational: CR from rank-300 to rank-1 | Fitting: OR ≤ rank ≤ CR | Opening Down: OR from rank+1 to rank+500")
        if category == "PwD":
            st.caption("*PwD Category*: Showing all PwD seats including OPEN(PwD), SC(PwD), OBC-NCL(PwD), etc.")
        st.caption("*NOTE* = For programs with Reservations/Categories, the OR AND CR shown correspond to Category Rank")
        st.caption("Scroll or open in fullscreen mode to see opening and closing ranks")
        
        table1_filter = base_filter & (
            (safe_numeric_filter(df, "CR", ">=", rank - 300) & safe_numeric_filter(df, "CR", "<", rank)) |
            (safe_numeric_filter(df, "OR", "<=", rank) & safe_numeric_filter(df, "CR", ">=", rank)) |
            (safe_numeric_filter(df, "OR", ">", rank) & safe_numeric_filter(df, "OR", "<=", rank + 500))
        )
        
        table1_df = df[table1_filter]
        display_table_with_sections(table1_df, rank, f"All Recommended {display_name} Programmes")
        
        st.markdown("---")
        st.subheader("⚡ Circuital Programmes")
        st.caption("Computer Science, Electrical, Electronics, Artificial Intelligence, Data Science, Mathematics and Computing, Instrumentation and Computational Engineering programmes")
        st.caption("Aspirational: CR from rank-300 to rank-1 | Fitting: OR ≤ rank ≤ CR | Opening Down: All available OR > rank")
        if category == "PwD":
            st.caption("*PwD Category*: Showing all PwD seats including OPEN(PwD), SC(PwD), OBC-NCL(PwD), etc.")
        st.caption("*NOTE* = For programs with Reservations/Categories, the OR AND CR shown correspond to Category Rank")
        st.caption("Scroll or open in fullscreen mode to see opening and closing ranks")
        
        circuital_keywords = ['Computer Science', 'Electrical', 'Electronics', 'Artificial', 'Mathematics', 'Instrumentation', 'Computational', 'Circuit', 'Data Science', 'CSE']
        circuital_pattern = '|'.join(circuital_keywords)
        
        table2_filter = base_filter & (
            df["Program"].str.contains(circuital_pattern, case=False, na=False)
        ) & (
            (safe_numeric_filter(df, "CR", ">=", rank - 300) & safe_numeric_filter(df, "CR", "<", rank)) |
            (safe_numeric_filter(df, "OR", "<=", rank) & safe_numeric_filter(df, "CR", ">=", rank)) |
            safe_numeric_filter(df, "OR", ">", rank)
        )
        
        table2_df = df[table2_filter]
        display_table_with_sections(table2_df, rank, f"Circuital {display_name} Programmes")
        

        if exam_type == "JEE Advanced":
            st.markdown("---")
            st.subheader("🏛️ Old 7 IITs Branches")
            st.caption("Old IITs: Bombay, Delhi, Kharagpur, Madras, Kanpur, Roorkee, Guwahati")
            st.caption("Aspirational: OR from rank-300 to rank-1 | Fitting: OR ≤ rank ≤ CR | Opening Down: All available OR > rank")
            if category == "PwD":
                st.caption("*PwD Category*: Showing all PwD seats including OPEN(PwD), SC(PwD), OBC-NCL(PwD), etc.")
            st.caption("*NOTE* = For programs with Reservations/Categories, the OR AND CR shown correspond to Category Rank")
            st.caption("Scroll or open in fullscreen mode to see opening and closing ranks")
            
            old_iits = ['Bombay', 'Delhi', 'Kharagpur', 'Madras', 'Kanpur', 'Roorkee', 'Guwahati']
            old_iits_pattern = '|'.join(old_iits)
            
            table3_filter = base_filter & (
                df["Institute"].str.contains(old_iits_pattern, case=False, na=False)
            ) & (
                (safe_numeric_filter(df, "OR", ">=", rank - 300) & safe_numeric_filter(df, "OR", "<", rank)) |
                (safe_numeric_filter(df, "OR", "<=", rank) & safe_numeric_filter(df, "CR", ">=", rank)) |
                safe_numeric_filter(df, "OR", ">", rank)
            )
            
            table3_df = df[table3_filter]
            display_table_with_sections(table3_df, rank, "Old 7 IITs Branches")
            
    except Exception as e:
        st.error(f"Error processing data: {e}")
        st.write("Please check your CSV file format and column names.")
        st.write("Error details:", str(e))
