import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="USA Store Search App", layout="wide")
st.title("🏬 USA Store Search App")

# Upload user file
uploaded_file = st.file_uploader("Upload your store list (Excel or CSV)", type=["xlsx", "csv"])

if uploaded_file:
    # Read the uploaded file
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Try extracting ZIP and State from address if not directly available
    if 'ZIP' not in df.columns or 'State' not in df.columns:
        def extract_zip(address):
            match = re.search(r'\b(\d{5})(?:[-\s]\d{4})?\b', str(address))
            return match.group(1) if match else None

        df['ZIP'] = df['Street Address-1'].apply(extract_zip)

        # Optional: add State extraction logic if needed

    # Sidebar filters
    st.sidebar.header("🔍 Search Filters")
    zip_filter = st.sidebar.text_input("Enter ZIP Code")
    state_filter = st.sidebar.text_input("Enter State Abbreviation (e.g., NY, TX)")
    name_filter = st.sidebar.text_input("Search by Store Name")

    # Apply filters
    filtered_df = df.copy()
    if zip_filter:
        filtered_df = filtered_df[filtered_df['ZIP'].astype(str).str.contains(zip_filter)]
    if state_filter:
        filtered_df = filtered_df[df.columns[df.columns.str.contains('State', case=False)][0]].str.upper().str.contains(state_filter.upper(), na=False)
    if name_filter:
        filtered_df = filtered_df[df.columns[df.columns.str.contains('Account Name', case=False)][0]].str.contains(name_filter, case=False, na=False)

    st.subheader("✅ Stores You Work With")
    st.dataframe(filtered_df)

    # Placeholder: Display external stores (to be fetched from web sources in future)
    st.subheader("🌐 Other Stores (Fetched from Web Sources - Coming Soon)")
    st.info("This section will show stores not in your list, pulled from external sources like Google Maps or Yelp.")

else:
    st.warning("Please upload your store list to begin.")
