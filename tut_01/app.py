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

    # Extract branch code from Roll (assuming first 2 letters are branch code after digits)
    # Example: 1401AI01 -> AI
    df["Branch"] = df["Roll"].str.extract(r'([A-Z]{2})')

    # Group by branch and save to CSV
    for branch, group in df.groupby("Branch"):
        file_path = os.path.join(output_dir, f"{branch}.csv")
        group.to_csv(file_path, index=False)

    st.success(f"Files saved in '{output_dir}' directory.")

    st.subheader("Generated Files")
    for branch in sorted(df["Branch"].unique()):
        st.write(f"{branch}.csv")
