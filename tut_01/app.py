import os
import math
import pandas as pd
import streamlit as st
from collections import defaultdict

st.title("📚 Student Branch & Group Segregator")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])
num_groups = st.number_input("Enter number of groups (for mixing)", min_value=1, step=1, value=5)

if uploaded_file is not None:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)

    # Extract branch code from Roll (e.g., 1401AI01 -> AI)
    df["Branch"] = df["Roll"].str.extract(r'([A-Z]{2})')

    # ----------------------------
    # PART 1: Branchwise Segregation
    # ----------------------------
    st.header("📌 Branchwise Segregation")

    output_dir_branch = "full_branchwise"
    os.makedirs(output_dir_branch, exist_ok=True)

    for branch, group in df.groupby("Branch"):
        file_path = os.path.join(output_dir_branch, f"{branch}.csv")
        group.to_csv(file_path, index=False)

        st.write(f"📂 **{branch}** → {len(group)} students")
        st.download_button(
            label=f"⬇️ Download {branch}.csv",
            data=group.to_csv(index=False).encode("utf-8"),
            file_name=f"{branch}.csv",
            mime="text/csv"
        )

    # ----------------------------
    # PART 2: Branchwise Group Mixer
    # ----------------------------
    if num_groups > 0:
        st.header("📌 Branchwise Group Mixer")

        total_students = len(df)
        per_group = math.ceil(total_students / num_groups)

        st.write(f"✅ Total students: {total_students}")
        st.write(f"✅ Groups: {num_groups}, Target per group: {per_group}")

        # Split branchwise into lists of indices
        branch_students = {b: list(g.index) for b, g in df.groupby("Branch")}

        groups = defaultdict(list)
        group_counts = pd.DataFrame(0, index=[f"G{i+1}" for i in range(num_groups)], 
                                    columns=sorted(df["Branch"].unique()) + ["Total"])

        # Round-robin allocation
        group_idx = 0
        while any(branch_students.values()):
            for branch, students in branch_students.items():
                if students:
                    student_idx = students.pop(0)
                    groups[group_idx].append(student_idx)

                    # update count matrix
                    group_name = f"G{group_idx+1}"
                    group_counts.loc[group_name, branch] += 1
                    group_counts.loc[group_name, "Total"] += 1

                    group_idx = (group_idx + 1) % num_groups

        # Save output dir
        output_dir_mix = "groupwise_mix"
        os.makedirs(output_dir_mix, exist_ok=True)

        st.subheader("Download Mixed Groups")
        for i in range(num_groups):
            group_name = f"G{i+1}"
            group_df = df.loc[groups[i]]
            file_path = os.path.join(output_dir_mix, f"{group_name}.csv")
            group_df.to_csv(file_path, index=False)

            st.write(f"📂 {group_name} → {len(group_df)} students")
            st.download_button(
                label=f"⬇️ Download {group_name}.csv",
                data=group_df.to_csv(index=False).encode("utf-8"),
                file_name=f"{group_name}.csv",
                mime="text/csv"
            )

        # Save summary matrix
        summary_file = os.path.join(output_dir_mix, "summary.csv")
        group_counts.to_csv(summary_file)

        st.subheader("📊 Group Summary Matrix")
        st.dataframe(group_counts)

        st.download_button(
            label="⬇️ Download Summary CSV",
            data=group_counts.to_csv().encode("utf-8"),
            file_name="summary.csv",
            mime="text/csv"
        )
