import streamlit as st
import pandas as pd
pip install streamlit pandas openpyxl


st.set_page_config(page_title="Store Finder", layout="wide")

st.title("🛍️ USA Retail Store Finder (Discount, Department, Convenience)")

uploaded_file = st.file_uploader("Upload your store list (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0)

        # Clean and extract ZIP & State (basic guess from address)
        df["ZIP Code"] = df["Street Address-1"].str.extract(r'(\b\d{5}\b)', expand=False)
        df["State"] = df["Street Address-1"].str.extract(r'\b([A-Z]{2})\b', expand=False)

        # Work status from Active/Inactive
        df["Work Status"] = df["Active/ Inactive"].apply(lambda x: "Yes" if str(x).strip().lower() == "active" else "No")

        # Sidebar filters
        st.sidebar.header("🔍 Filter Stores")
        zip_filter = st.sidebar.text_input("Search by ZIP Code")
        state_filter = st.sidebar.text_input("Search by State (e.g., NY, TX)")
        name_filter = st.sidebar.text_input("Search by Store Name")

        # Apply filters
        filtered_df = df.copy()
        if zip_filter:
            filtered_df = filtered_df[filtered_df["ZIP Code"] == zip_filter.strip()]
        if state_filter:
            filtered_df = filtered_df[filtered_df["State"] == state_filter.strip().upper()]
        if name_filter:
            filtered_df = filtered_df[filtered_df["Account Name / Customer Name"].str.contains(name_filter, case=False, na=False)]

        st.subheader(f"📍 Results ({len(filtered_df)} stores found)")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ✅ Stores You Work With")
            worked_df = filtered_df[filtered_df["Work Status"] == "Yes"]
            st.dataframe(worked_df[["Account Name / Customer Name", "Street Address-1", "ZIP Code", "State"]])

        with col2:
            st.markdown("### ❌ Stores You Don't Work With")
            not_worked_df = filtered_df[filtered_df["Work Status"] == "No"]
            st.dataframe(not_worked_df[["Account Name / Customer Name", "Street Address-1", "ZIP Code", "State"]])

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("📤 Upload your store list to get started.")
