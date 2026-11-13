import streamlit as st
import pandas as pd

st.set_page_config(page_title="Apex Market Intelligence Engine", layout="wide")
st.title("🦅 Apex Market Intelligence Engine")
st.write("System Status: **ONLINE**. Ready for branch manifest ingestion.")
st.divider()

# Provide a 1-click sample file for prospects testing the app
sample_data = pd.DataFrame({
    "Property Address": ["14 Oak Avenue, Liverpool", "82 Marine Crescent, Waterloo", "5 Church Road, Crosby"],
    "Our Price": ["£325,000", "£450,000", "£210,000"],
    "Competitor Price": ["£315,000", "£450,000", "£199,950"],
    "Competitor Website": ["https://rightmove.co.uk", "https://zoopla.co.uk", "rightmove.co.uk"]
})

st.download_button(
    label="📥 Download Sample CSV Template",
    data=sample_data.to_csv(index=False),
    file_name="apex_sample_manifest.csv",
    mime="text/csv"
)

uploaded_file = st.file_uploader("Upload your weekly branch manifest (.csv):", type=["csv"])

def clean_price(val):
    if pd.isna(val):
        return 0.0
    cleaned = str(val).replace("£", "").replace(",", "").strip()
    return float(cleaned)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    required_columns = ["Property Address", "Our Price", "Competitor Price", "Competitor Website"]
    
    if all(col in df.columns for col in required_columns):
        df["Clean Our Price"] = df["Our Price"].apply(clean_price)
        df["Clean Comp Price"] = df["Competitor Price"].apply(clean_price)
        df["Price Difference"] = df["Clean Our Price"] - df["Clean Comp Price"]
        
        undercut_df = df[df["Price Difference"] > 0].copy()
        
        # Executive KPI Strip
        col1, col2, col3 = st.columns(3)
        col1.metric("Properties Audited", len(df))
        col2.metric("Undercut Listings", len(undercut_df), delta=f"-{len(undercut_df)} Alerts", delta_color="inverse")
        col3.metric("Total Price Gap", f"£{undercut_df['Price Difference'].sum():,.2f}")
        
        st.divider()
        st.subheader("📊 Live Market Position Analysis")
        
        for _, row in df.iterrows():
            address = row["Property Address"]
            diff = row["Price Difference"]
            site = str(row["Competitor Website"]).strip()
            if not site.startswith("http"):
                site = f"https://{site}"
                
            if diff > 0:
                st.error(f"⚠️ **{address}** | Undercut by **£{diff:,.2f}** | Source: [{site}]({site})")
            else:
                st.success(f"✅ **{address}** | Competitive against [{site}]({site})")
    else:
        st.warning(f"⚠️ Invalid spreadsheet layout. Ensure columns match: {required_columns}")
else:
    st.info("💡 Drop the active branch tracking file into the box above—or download the sample CSV to test the engine.")
