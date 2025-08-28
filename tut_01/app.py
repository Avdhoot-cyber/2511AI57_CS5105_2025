import streamlit as st
import pandas as pd
from io import BytesIO
import re
from collections import deque
import math
import os

st.set_page_config(page_title="Group Stats Generator", page_icon="📊", layout="wide")
st.title("Group Stats Generator")
st.caption("Upload one Excel file with all students (Roll, Name, Email) and get group-wise stats + download.")

DEFAULT_GROUPS = 15
branches_order = ["AI","CB","CE","CH","CS","CT","EC","MC","MM","MT"]

# (keep helper functions: extract_branch, make_stats, mixed_strategy, uniform_strategy)
# copy your existing helper functions here (omitted for brevity in this snippet)
# — ensure they are present in the file unchanged

# --- (paste your helper functions from previous file here) ---
# extract_branch, make_stats, mixed_strategy, uniform_strategy
# ... (exact same as before) ...

# For brevity in this message, assume the helper functions are the same as in your current file.
def extract_branch(roll):
    match = re.search(r'([A-Z]{2})', str(roll))
    return match.group(1) if match else None
    
def run():
    uploaded_file = st.file_uploader("Upload input_Make Groups.xlsx", type=["xlsx"])
    n_groups = st.number_input("Number of groups", min_value=2, max_value=100, value=DEFAULT_GROUPS, step=1)

    if not uploaded_file:
        return

    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f" Could not read file: {e}")
        return

    for col in ["Roll","Name","Email"]:
        if col not in df.columns:
            df[col] = ""
    df["Branch"] = df["Roll"].apply(extract_branch)

    # --- Branchwise CSVs (full_branchwise) ---
    output_dir_branch = "full_branchwise"
    os.makedirs(output_dir_branch, exist_ok=True)

    for branch, group in df.groupby("Branch"):
        branch_file = os.path.join(output_dir_branch, f"{branch}.csv")
        group.to_csv(branch_file, index=False)

    st.success(f"Saved branch CSVs to ./{output_dir_branch}/")

    # --- Create mixed & uniform groups ---
    mixed_groups = mixed_strategy(df, n_groups)
    uniform_groups = uniform_strategy(df, n_groups)

    # Make directories for group outputs
    output_dir_mixed = "group_branchwise_mix"
    output_dir_uniform = "group_uniform_mix"
    os.makedirs(output_dir_mixed, exist_ok=True)
    os.makedirs(output_dir_uniform, exist_ok=True)

    # Save mixed groups as CSVs
    for i, group_rows in enumerate(mixed_groups, start=1):
        gdf = pd.DataFrame(group_rows)
        file_path = os.path.join(output_dir_mixed, f"G{i}.csv")
        if not gdf.empty:
            gdf.to_csv(file_path, index=False)
        else:
            # create empty CSV with headers to keep folder consistent
            pd.DataFrame(columns=["Roll","Name","Email","Branch"]).to_csv(file_path, index=False)

    # Save uniform groups as CSVs
    for i, group_rows in enumerate(uniform_groups, start=1):
        gdf = pd.DataFrame(group_rows)
        file_path = os.path.join(output_dir_uniform, f"G{i}.csv")
        if not gdf.empty:
            gdf.to_csv(file_path, index=False)
        else:
            pd.DataFrame(columns=["Roll","Name","Email","Branch"]).to_csv(file_path, index=False)

    st.success(f"Saved mixed groups to ./{output_dir_mixed}/ and uniform groups to ./{output_dir_uniform}/")

    # --- Display counts and provide downloads (in-memory) ---
    st.subheader("Branch files (counts + download)")
    for branch, group in df.groupby("Branch"):
        st.write(f"📌 **{branch}** → {len(group)} students")
        st.download_button(
            label=f"⬇️ Download {branch}.csv",
            data=group.to_csv(index=False).encode("utf-8"),
            file_name=f"{branch}.csv",
            mime="text/csv"
        )

    st.subheader("Mixed Groups (download individual CSVs)")
    for i, group_rows in enumerate(mixed_groups, start=1):
        gdf = pd.DataFrame(group_rows)
        st.write(f"Group G{i} → {len(gdf)} students")
        st.download_button(
            label=f"⬇️ Download Mixed_G{i}.csv",
            data=gdf.to_csv(index=False).encode("utf-8"),
            file_name=f"Mixed_G{i}.csv",
            mime="text/csv"
        )

    st.subheader("Uniform Groups (download individual CSVs)")
    for i, group_rows in enumerate(uniform_groups, start=1):
        gdf = pd.DataFrame(group_rows)
        st.write(f"Group G{i} → {len(gdf)} students")
        st.download_button(
            label=f"⬇️ Download Uniform_G{i}.csv",
            data=gdf.to_csv(index=False).encode("utf-8"),
            file_name=f"Uniform_G{i}.csv",
            mime="text/csv"
        )

    # --- Also produce consolidated Excel with stats & sheets ---
    stats_mixed = make_stats(mixed_groups, n_groups)
    stats_uniform = make_stats(uniform_groups, n_groups)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        stats_mixed.to_excel(writer, sheet_name="Stats_Mixed", index=False)
        stats_uniform.to_excel(writer, sheet_name="Stats_Uniform", index=False)
        # Mixed sheets
        for gi, group_rows in enumerate(mixed_groups, start=1):
            gdf = pd.DataFrame(group_rows)
            if not gdf.empty:
                gdf.to_excel(writer, sheet_name=f"Mixed_G{gi}", index=False)
            else:
                pd.DataFrame(columns=["Roll","Name","Email","Branch"]).to_excel(writer, sheet_name=f"Mixed_G{gi}", index=False)
        # Uniform sheets
        for gi, group_rows in enumerate(uniform_groups, start=1):
            gdf = pd.DataFrame(group_rows)
            if not gdf.empty:
                gdf.to_excel(writer, sheet_name=f"Uniform_G{gi}", index=False)
            else:
                pd.DataFrame(columns=["Roll","Name","Email","Branch"]).to_excel(writer, sheet_name=f"Uniform_G{gi}", index=False)
    output.seek(0)

    st.subheader("Download consolidated Excel")
    st.download_button(
        label="⬇ Download output.xlsx",
        data=output,
        file_name="output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

if __name__ == "__main__":
    run()

