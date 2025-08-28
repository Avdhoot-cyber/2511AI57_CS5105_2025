import streamlit as st
import pandas as pd
import re
from collections import deque
import math
from io import BytesIO

# --------------------- #
# 🎨 Streamlit Page Setup
# --------------------- #
st.set_page_config(page_title="Student Grouping Tool", page_icon="📊", layout="wide")

# Add custom CSS for styling
st.markdown("""
    <style>
    body {
        background-color: #f9fafc;
        font-family: 'Segoe UI', sans-serif;
    }
    .main {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
    }
    h1, h2, h3, h4 {
        color: #2c3e50;
    }
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Student Grouping Tool")
st.caption("Upload an Excel file with student details to generate balanced group distributions.")


# --------------------- #
# 🔹 Utility Functions
# --------------------- #
PREFERRED_BRANCH_ORDER = ["AI", "CB", "CE", "CH", "CS", "CT", "EC", "MC", "MM", "MT"]


def extract_department(roll_no: str) -> str:
    """Pull department code (2 capital letters) from roll number string."""
    if pd.isna(roll_no):
        return "??"
    match = re.search(r"[A-Z]{2}", str(roll_no))
    return match.group(0) if match else "??"


def compile_statistics(group_list, total_groups):
    """Create a summary table showing department counts per group."""
    all_depts = sorted(set().union(*[set(pd.DataFrame(g)["Department"]) for g in group_list if g]))

    stats = pd.DataFrame(0, index=[f"Group {i+1}" for i in range(total_groups)],
                         columns=all_depts + ["Total"])

    for idx, members in enumerate(group_list, start=1):
        gdf = pd.DataFrame(members)
        if not gdf.empty:
            for dept in all_depts:
                stats.loc[f"Group {idx}", dept] = int((gdf["Department"] == dept).sum())
            stats.loc[f"Group {idx}", "Total"] = len(gdf)

    return stats.reset_index().rename(columns={"index": "Group"})


# --------------------- #
# 🔹 Grouping Algorithms
# --------------------- #
def branch_round_robin(data, total_groups):
    """Distribute students round-robin by department."""
    seen_depts = list(pd.unique(data["Department"]))

    cycle = [d for d in PREFERRED_BRANCH_ORDER if d in seen_depts] + \
            [d for d in seen_depts if d not in PREFERRED_BRANCH_ORDER]

    queues = {d: deque(data[data["Department"] == d].to_dict("records")) for d in cycle}

    total_students = len(data)
    base_size = total_students // total_groups
    remainder = total_students % total_groups
    group_targets = [base_size + (1 if i < remainder else 0) for i in range(total_groups)]

    groups = [[] for _ in range(total_groups)]

    for gi in range(total_groups):
        target_size = group_targets[gi]
        while len(groups[gi]) < target_size:
            progress = False
            for dept in cycle:
                if len(groups[gi]) >= target_size:
                    break
                if queues[dept]:
                    groups[gi].append(queues[dept].popleft())
                    progress = True
            if not progress:
                break

    return groups


def uniform_fill(data, total_groups):
    """Try to fill groups uniformly while keeping departments clustered."""
    total = len(data)
    group_capacity = math.ceil(total / total_groups)
    groups = []

    dept_counts = data["Department"].value_counts()
    sorted_depts = list(dept_counts.sort_values(ascending=False).index)

    dept_rows = {d: data[data["Department"] == d].to_dict("records") for d in sorted_depts}
    leftovers = []

    # Full department groups first
    for dept, rows in dept_rows.items():
        n = len(rows)
        idx = 0
        while n - idx >= group_capacity:
            groups.append(rows[idx: idx + group_capacity])
            idx += group_capacity
        if idx < n:
            leftovers.append(rows[idx:])

    leftovers = deque(sorted(leftovers, key=lambda x: -len(x)))

    # Merge leftover blocks into groups
    while leftovers:
        block = leftovers.popleft()
        new_group = list(block)
        space = group_capacity - len(new_group)

        while space > 0 and leftovers:
            nxt = leftovers.popleft()
            if len(nxt) <= space:
                new_group.extend(nxt)
                space -= len(nxt)
            else:
                new_group.extend(nxt[:space])
                leftovers.appendleft(nxt[space:])
                space = 0
        groups.append(new_group)

    while len(groups) < total_groups:
        groups.append([])

    return groups


# --------------------- #
# 🔹 Streamlit Application
# --------------------- #
def main():
    file = st.file_uploader("📥 Upload Excel File", type=["xlsx"])
    num_groups = st.number_input("Number of Groups", min_value=2, max_value=100, value=15)

    if file:
        try:
            df = pd.read_excel(file)
        except Exception as e:
            st.error(f"❌ Could not read the file: {e}")
            return

        # Ensure required columns
        for col in ["Roll", "Name", "Email"]:
            if col not in df.columns:
                df[col] = ""

        df["Department"] = df["Roll"].apply(extract_department)

        # Generate groups
        rr_groups = branch_round_robin(df, num_groups)
        rr_stats = compile_statistics(rr_groups, num_groups)

        uniform_groups = uniform_fill(df, num_groups)
        uniform_stats = compile_statistics(uniform_groups, num_groups)

        # Show summary stats
        st.subheader("📊 Branch-wise Round Robin Distribution")
        st.dataframe(rr_stats, use_container_width=True, hide_index=True)

        st.subheader("📊 Uniform Department Clustering")
        st.dataframe(uniform_stats, use_container_width=True, hide_index=True)

        # Preview groups
        with st.expander("👀 Preview Round Robin Groups"):
            for gi, g in enumerate(rr_groups, start=1):
                st.markdown(f"### Group {gi}")
                gdf = pd.DataFrame(g)
                st.dataframe(gdf[["Roll", "Name", "Email", "Department"]],
                             use_container_width=True, hide_index=True)

        with st.expander("👀 Preview Uniform Groups"):
            for gi, g in enumerate(uniform_groups, start=1):
                st.markdown(f"### Group {gi}")
                gdf = pd.DataFrame(g)
                st.dataframe(gdf[["Roll", "Name", "Email", "Department"]],
                             use_container_width=True, hide_index=True)

        # Export to Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            rr_stats.to_excel(writer, sheet_name="Stats_RR", index=False)
            uniform_stats.to_excel(writer, sheet_name="Stats_Uniform", index=False)

            for gi, g in enumerate(rr_groups, start=1):
                pd.DataFrame(g).to_excel(writer, sheet_name=f"RR_Group{gi}", index=False)
            for gi, g in enumerate(uniform_groups, start=1):
                pd.DataFrame(g).to_excel(writer, sheet_name=f"Uniform_Group{gi}", index=False)

        buffer.seek(0)

        st.download_button(
            label="⬇️ Download Grouped Data",
            data=buffer,
            file_name="grouped_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# --------------------- #
# 🚀 Run App
# --------------------- #
if __name__ == "__main__":
    main()
