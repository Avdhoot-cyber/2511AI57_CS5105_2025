import os
import pandas as pd
import streamlit as st

st.title("Branchwise Student Segregator")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)

    # Make directory for outputs
    output_dir = "full_branchwise"
    os.makedirs(output_dir, exist_ok=True)

    # Extract branch code from Roll (e.g., 1401AI01 -> AI)
    df["Branch"] = df["Roll"].str.extract(r'([A-Z]{2})')

    st.subheader("Generated Branch Files")

    for branch, group in df.groupby("Branch"):
        file_path = os.path.join(output_dir, f"{branch}.csv")
        group.to_csv(file_path, index=False)

        # Show count + download button
        st.write(f"📌 **{branch}** → {len(group)} students")
        st.download_button(
            label=f"⬇️ Download {branch}.csv",
            data=group.to_csv(index=False).encode("utf-8"),
            file_name=f"{branch}.csv",
            mime="text/csv"
        )
