import streamlit as st
import pandas as pd
from io import BytesIO
import re
from collections import deque
import math

# --- Page Config ---
st.set_page_config(page_title="Group Stats Generator", page_icon="📊", layout="wide")

# --- Custom CSS ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-family: 'Segoe UI', sans-serif;
    }
    .main {
        background-color: #f9f9fb;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        color: #333 !important;
    }
    h1, h2, h3, h4 {
        color: #2c3e50;
        font-weight: 700;
    }
    .stDownloadButton button {
        background: #667eea;
        color: white;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-size: 16px;
        border: none;
        transition: 0.3s;
    }
    .stDownloadButton button:hover {
        background: #764ba2;
        transform: scale(1.05);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-card h3 {
        margin: 0;
        font-size: 14px;
        color: #555;
    }
    .metric-card p {
        margin: 0;
        font-size: 22px;
        font-weight: 700;
        color: #667eea;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        border-radius: 10px;
        overflow: hidden;
    }
    th {
        background: #667eea !important;
        color: white !important;
        text-align: center !important;
    }
    td {
        background: #fdfdfd !important;
        text-align: center !important;
    }
    tr:nth-child(even) td {
        background: #f4f6fa !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Helper functions ---
DEFAULT_GROUPS = 15
branches_order = ["AI","CB","CE","CH","CS","CT","EC","MC","MM","MT"]

def extract_branch(roll: str) -> str:
    if pd.isna(roll): return "??"
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
            for b in branch_cycle:
                if len(groups[gi]) >= targets[gi]: break
                if queues[b]: groups[gi].append(queues[b].popleft())
    return groups

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
        if i < len(rows): leftover_blocks.append(rows[i:])
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
    while len(groups) < n_groups: groups.append([])
    return groups

# --- Main ---
def run():
    st.markdown("<h1 style='text-align:center;'>📊 Group Stats Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>Upload an Excel file and get automatically generated balanced groups.</p>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])
    n_groups = st.slider("🔢 Select Number of Groups", min_value=2, max_value=50, value=DEFAULT_GROUPS, step=1)

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        for col in ["Roll","Name","Email"]: 
            if col not in df.columns: df[col] = ""
        df["Branch"] = df["Roll"].apply(extract_branch)

        mixed_groups, uniform_groups = mixed_strategy(df, n_groups), uniform_strategy(df, n_groups)
        stats_mixed, stats_uniform = make_stats(mixed_groups, n_groups), make_stats(uniform_groups, n_groups)

        # --- Metric Cards ---
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='metric-card'><h3>Students</h3><p>{len(df)}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><h3>Groups</h3><p>{n_groups}</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><h3>Avg / Group</h3><p>{len(df)/n_groups:.2f}</p></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-card'><h3>Branches</h3><p>{df['Branch'].nunique()}</p></div>", unsafe_allow_html=True)

        # --- Stats Display ---
        st.subheader("📊 Mixed Strategy (Balanced RR)")
        st.dataframe(stats_mixed, use_container_width=True, hide_index=True)

        st.subheader("📊 Uniform Strategy (Block)")
        st.dataframe(stats_uniform, use_container_width=True, hide_index=True)

        # --- Group Previews ---
        st.markdown("### 👥 Preview Groups")
        tabs = st.tabs(["🔄 Mixed Groups", "⚖️ Uniform Groups"])
        with tabs[0]:
            for gi, group_rows in enumerate(mixed_groups, start=1):
                st.markdown(f"**Group {gi}**")
                st.dataframe(pd.DataFrame(group_rows)[["Roll","Name","Email","Branch"]], use_container_width=True, hide_index=True)
        with tabs[1]:
            for gi, group_rows in enumerate(uniform_groups, start=1):
                st.markdown(f"**Group {gi}**")
                st.dataframe(pd.DataFrame(group_rows)[["Roll","Name","Email","Branch"]], use_container_width=True, hide_index=True)

        # --- Excel Output ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            stats_mixed.to_excel(writer, sheet_name="Stats_Mixed", index=False)
            stats_uniform.to_excel(writer, sheet_name="Stats_Uniform", index=False)
            for gi, group_rows in enumerate(mixed_groups, start=1):
                gdf = pd.DataFrame(group_rows)
                if not gdf.empty: gdf.to_excel(writer, sheet_name=f"Mixed_G{gi}", index=False)
            for gi, group_rows in enumerate(uniform_groups, start=1):
                gdf = pd.DataFrame(group_rows)
                if not gdf.empty: gdf.to_excel(writer, sheet_name=f"Uniform_G{gi}", index=False)
        output.seek(0)

        st.download_button(
            label="⬇ Download Groups Excel",
            data=output,
            file_name="groups_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

run()
