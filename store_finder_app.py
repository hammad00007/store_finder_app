import streamlit as st
import pandas as pd
import re
import requests

st.set_page_config(page_title="USA Store Search App", layout="wide")
st.title("🏬 USA Store Search App")

# API KEY - Replace with st.secrets["google_api_key"] or env var for security
GOOGLE_API_KEY = "AIzaSyDSxVYzLQdlFINRyzdrnWZDjLxeMYVza7Q"

# Upload user file
uploaded_file = st.file_uploader("Upload your store list (Excel or CSV)", type=["xlsx", "csv"])

if uploaded_file:
    # Read the uploaded file
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    # Clean and normalize column names
    df.columns = df.columns.str.strip().str.replace(r"[^\w]+", "_", regex=True)

    # Try extracting ZIP and State from address if not directly available
    if 'ZIP' not in df.columns:
        def extract_zip(address):
            match = re.search(r'\b(\d{5})(?:[-\s]\d{4})?\b', str(address))
            return match.group(1) if match else None
        address_col = [col for col in df.columns if 'address' in col.lower()]
        if address_col:
            df['ZIP'] = df[address_col[0]].apply(extract_zip)

    # Sidebar filters
    st.sidebar.header("🔍 Search Filters")
    zip_filter = st.sidebar.text_input("Enter ZIP Code")
    state_filter = st.sidebar.text_input("Enter State Abbreviation (e.g., NY, TX)")
    name_filter = st.sidebar.text_input("Search by Store Name")
    store_type = st.sidebar.selectbox("Select Store Type (for Google Search)", ["convenience store", "discount store", "department store"])

    # Apply filters to user's store list
    filtered_df = df.copy()
    if zip_filter:
        filtered_df = filtered_df[filtered_df['ZIP'].astype(str).str.contains(zip_filter)]
    if state_filter:
        state_col = [col for col in df.columns if 'state' in col.lower()]
        if state_col:
            filtered_df = filtered_df[filtered_df[state_col[0]].str.upper().str.contains(state_filter.upper(), na=False)]
    if name_filter:
        name_col = [col for col in df.columns if 'account_name' in col.lower()]
        if name_col:
            filtered_df = filtered_df[filtered_df[name_col[0]].str.contains(name_filter, case=False, na=False)]

    st.subheader("✅ Stores You Work With")
    st.dataframe(filtered_df)

    # Fetch external stores using Google Places API
    st.subheader("🌐 Other Stores from Google Places API")
    if zip_filter:
        query = f"{store_type} in {zip_filter}"
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "key": GOOGLE_API_KEY
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            places_data = response.json()
            if "results" in places_data:
                results = places_data["results"]
                external_df = pd.DataFrame([{
                    "Name": place.get("name"),
                    "Address": place.get("formatted_address"),
                    "Rating": place.get("rating"),
                    "User Ratings": place.get("user_ratings_total"),
                    "Place ID": place.get("place_id")
                } for place in results])
                st.dataframe(external_df)
            else:
                st.info("No stores found from Google for this ZIP code.")
        else:
            st.error("Failed to fetch data from Google Places API.")

else:
    st.warning("Please upload your store list to begin.")
