import streamlit as st
import pandas as pd
from io import BytesIO
import re
from collections import deque
import math

# --- Page Config ---
st.set_page_config(page_title="Group Stats Generator", page_icon="📊", layout="wide")

st.markdown("<h1 style='text-align:center; color:#4CAF50;'>📊 Group Stats Generator</h1>", unsafe_allow_html=True)
st.caption("Upload one Excel file with all students (Roll, Name, Email) and get group-wise stats + download.")

DEFAULT_GROUPS = 15
branches_order = ["AI","CB","CE","CH","CS","CT","EC","MC","MM","MT"]

# --- Helper functions ---
def extract_branch(roll: str) -> str:
    if pd.isna(roll):
        return "??"
    match = re.search(r"[A-Z]{2}", str(roll))
    return match.group(0) if match else "??"

def make_stats(groups, n_groups):
    all_branches = sorted(set().union(*[set(pd.DataFrame(g)["Branch"]) for g in groups if g]))
    stats = pd.DataFrame(0, index=[f"G{i+1}" for i in range(n_groups)], columns=all_branches + ["Total"])
    for gi, group_rows in enumerate(groups, start=1):
        gdf = pd.DataFrame(group_rows)
        if not gdf.empty:
            for b in all_branches:
                stats.loc[f"G{gi}", b] = int((gdf["Branch"] == b).sum())
            stats.loc[f"G{gi}", "Total"] = int(len(gdf))
    return stats.reset_index().rename(columns={"index": "Group"})

# --- Mixed Strategy ---
def mixed_strategy(df, n_groups):
    present_branches = list(pd.unique(df["Branch"]))
    branch_cycle = [b for b in branches_order if b in present_branches] + \
                   [b for b in present_branches if b not in branches_order]
    queues = {b: deque([row for _, row in df[df["Branch"] == b].iterrows()]) for b in branch_cycle}
    total = len(df)
    base, rem = divmod(total, n_groups)
    targets = [base + (1 if i < rem else 0) for i in range(n_groups)]
    groups = [[] for _ in range(n_groups)]
    for gi in range(n_groups):
        while len(groups[gi]) < targets[gi]:
            progress = False
            for b in branch_cycle:
                if len(groups[gi]) >= targets[gi]:
                    break
                if queues[b]:
                    groups[gi].append(queues[b].popleft())
                    progress = True
            if not progress:
                break
    return groups

# --- Uniform Strategy ---
def uniform_strategy(df, n_groups):
    total = len(df)
    group_size = math.ceil(total / n_groups)
    groups, leftover_blocks = [], []
    counts = df["Branch"].value_counts()
    sorted_branches = list(counts.sort_values(ascending=False).index)
    branch_rows = {b: [row for _, row in df[df["Branch"] == b].iterrows()] for b in sorted_branches}
    for b in sorted_branches:
        rows, i = branch_rows[b], 0
        while len(rows) - i >= group_size:
            groups.append(rows[i:i+group_size]); i += group_size
        if i < len(rows):
            leftover_blocks.append(rows[i:])
    leftover_blocks = deque(sorted(leftover_blocks, key=lambda blk: -len(blk)))
    while leftover_blocks:
        largest_block = leftover_blocks.popleft()
        current_group, space = list(largest_block), group_size - len(largest_block)
        while space > 0 and leftover_blocks:
            block = leftover_blocks.popleft()
            if len(block) <= space:
                current_group.extend(block); space -= len(block)
            else:
                current_group.extend(block[:space])
                leftover_blocks.appendleft(block[space:]); space = 0
        groups.append(current_group)
    if len(groups) > n_groups:
        raise ValueError(f"Created {len(groups)} groups but expected {n_groups}")
    while len(groups) < n_groups:
        groups.append([])
    return groups

# --- Main app ---
def run():
    uploaded_file = st.file_uploader("📂 Upload input_Make Groups.xlsx", type=["xlsx"])
    n_groups = st.number_input("🔢 Number of groups", min_value=2, max_value=100, value=DEFAULT_GROUPS, step=1)

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"❌ Could not read file: {e}")
            return

        for col in ["Roll","Name","Email"]:
            if col not in df.columns:
                df[col] = ""
        df["Branch"] = df["Roll"].apply(extract_branch)

        mixed_groups, stats_mixed = mixed_strategy(df, n_groups), None
        stats_mixed = make_stats(mixed_groups, n_groups)
        uniform_groups, stats_uniform = uniform_strategy(df, n_groups), None
        stats_uniform = make_stats(uniform_groups, n_groups)

        # --- Metrics ---
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👨‍🎓 Students", f"{len(df)}")
        c2.metric("👥 Groups", f"{n_groups}")
        c3.metric("📏 Avg / Group", f"{(len(df)/n_groups):.2f}")
        c4.metric("🏷️ Branches", f"{df['Branch'].nunique()}")

        # --- Tabs for cleaner UI ---
        tabs = st.tabs(["📊 Stats", "👥 Group Previews", "📂 Download Output"])

        with tabs[0]:
            st.subheader("📊 Stats - Mixed Strategy (Branch-wise RR)")
            st.dataframe(stats_mixed.style.background_gradient(cmap="YlGnBu"), use_container_width=True)

            st.subheader("📊 Stats - Uniform Strategy")
            st.dataframe(stats_uniform.style.background_gradient(cmap="OrRd"), use_container_width=True)

        with tabs[1]:
            mtab, utab = st.tabs(["🔄 Mixed Groups", "⚖️ Uniform Groups"])
            with mtab:
                for gi, group_rows in enumerate(mixed_groups, start=1):
                    st.markdown(f"**Group {gi}**")
                    gdf = pd.DataFrame(group_rows)
                    st.dataframe(gdf[["Roll","Name","Email","Branch"]], use_container_width=True, hide_index=True)
            with utab:
                for gi, group_rows in enumerate(uniform_groups, start=1):
                    st.markdown(f"**Group {gi}**")
                    gdf = pd.DataFrame(group_rows)
                    st.dataframe(gdf[["Roll","Name","Email","Branch"]], use_container_width=True, hide_index=True)

        with tabs[2]:
            # --- Save Excel ---
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                stats_mixed.to_excel(writer, sheet_name="Stats_Mixed", index=False)
                stats_uniform.to_excel(writer, sheet_name="Stats_Uniform", index=False)
                for gi, group_rows in enumerate(mixed_groups, start=1):
                    gdf = pd.DataFrame(group_rows)
                    if not gdf.empty:
                        gdf.to_excel(writer, sheet_name=f"Mixed_G{gi}", index=False)
                for gi, group_rows in enumerate(uniform_groups, start=1):
                    gdf = pd.DataFrame(group_rows)
                    if not gdf.empty:
                        gdf.to_excel(writer, sheet_name=f"Uniform_G{gi}", index=False)
            output.seek(0)

            st.success("✅ Output file is ready!")
            st.download_button(
                label="⬇ Download output.xlsx",
                data=output,
                file_name="output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            # Preview sheets
            st.info("Preview of output.xlsx (Stats only)")
            st.dataframe(stats_mixed, use_container_width=True, hide_index=True)

run()
