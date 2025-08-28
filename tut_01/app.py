import pandas as pd
import streamlit as st
import io

st.title("📚 Branchwise Student Segregator")

# File uploader
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Read Excel file
    df = pd.read_excel(uploaded_file)

    st.subheader("Uploaded Data")
    st.dataframe(df)

    # Extract branch from Roll number (e.g., 1401AI01 -> AI)
    df["Branch"] = df["Roll"].str.extract(r'([A-Z]{2})')

    st.subheader("Branchwise Student Data")

    # Group students by branch
    for branch, group in df.groupby("Branch"):
        st.markdown(f"### 🏷️ {branch} — {len(group)} students")

        # Show preview
        st.dataframe(group)

        # Convert group to CSV (in memory)
        csv_buffer = io.StringIO()
        group.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")

        # Download button
        st.download_button(
            label=f"⬇️ Download {branch}.csv",
            data=csv_bytes,
            file_name=f"{branch}.csv",
            mime="text/csv"
        )
