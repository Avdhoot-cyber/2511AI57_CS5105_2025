import streamlit as st
import pandas as pd
from io import BytesIO
import re
from collections import deque
import math

st.set_page_config(page_title="Group Stats Generator", page_icon=" ", layout="wide")

st.title("Group Stats Generator")
st.caption("Upload one Excel file with all students (Roll, Name, Email) and get group-wise stats + download.")

DEFAULT_GROUPS = 15
branches_order = ["AI","CB","CE","CH","CS","CT","EC","MC","MM","MT"]  # desired display order

# --- Helper functions ---
def extract_branch(roll: str) -> str:
    """Extract 2-letter branch code from Roll string."""
    if pd.isna(roll):
        return "??"
    match = re.search(r"[A-Z]{2}", str(roll))
    return match.group(0) if match else "??"

def make_stats(groups, n_groups):
    """Generate stats table from groups list."""
    # Collect all branches dynamically
    all_branches = sorted(set().union(*[set(pd.DataFrame(g)["Branch"]) for g in groups if g]))
    
    stats = pd.DataFrame(0, index=[f"G{i+1}" for i in range(n_groups)], columns=all_branches + ["Total"])
    
    for gi, group_rows in enumerate(groups, start=1):
        gdf = pd.DataFrame(group_rows)
        if not gdf.empty:
            for b in all_branches:
                stats.loc[f"G{gi}", b] = int((gdf["Branch"] == b).sum())
            stats.loc[f"G{gi}", "Total"] = int(len(gdf))
    
    return stats.reset_index().rename(columns={"index": "Group"})


# --- Mixed Strategy: Branch-wise Round Robin per GROUP (your requirement) ---
def mixed_strategy(df, n_groups):
    
    # Per-branch queues in original file order
    present_branches = list(pd.unique(df["Branch"]))  # preserves first-seen order in file
    # Use your preferred branch order first, then any extra branches (if present in data)
    branch_cycle = [b for b in branches_order if b in present_branches] + \
                   [b for b in present_branches if b not in branches_order]

    queues = {}
    for b in branch_cycle:
        bdf = df[df["Branch"] == b]
        # Keep original order within branch as in the uploaded file
        queues[b] = deque([row for _, row in bdf.iterrows()])

    total = len(df)
    base = total // n_groups
    rem = total % n_groups
    # Balanced target sizes (first 'rem' groups get +1)
    targets = [base + (1 if i < rem else 0) for i in range(n_groups)]

    groups = [[] for _ in range(n_groups)]

    # Fill each group to its target using branch-wise round robin cycles
    for gi in range(n_groups):
        target = targets[gi]
        if target == 0:
            continue
        
        while len(groups[gi]) < target:
            progress = False
            for b in branch_cycle:
                if len(groups[gi]) >= target:
                    break
                if queues[b]:
                    row = queues[b].popleft()
                    groups[gi].append(row)
                    progress = True
            if not progress:
               
                break

    return groups

# --- Uniform strategy (unchanged) ---
def uniform_strategy(df, n_groups):
    
    total = len(df)
    group_size = math.ceil(total / n_groups)
    groups = []

    # Branch counts sorted decreasing
    counts = df["Branch"].value_counts()
    sorted_branches = list(counts.sort_values(ascending=False).index)

    # Preserve order within each branch
    branch_rows = {b: [row for _, row in df[df["Branch"] == b].iterrows()]
                   for b in sorted_branches}

    leftover_blocks = []  

    # Step 1: make full mono-branch groups and collect leftover blocks
    for b in sorted_branches:
        rows = branch_rows[b]
        n = len(rows)
        i = 0
        while n - i >= group_size:
            groups.append(rows[i:i+group_size])  # full group (one branch)
            i += group_size
        if i < n:
            # leftover block for this branch (kept together initially)
            leftover_blocks.append(rows[i:])

   
    leftover_blocks = sorted(leftover_blocks, key=lambda blk: -len(blk))
    leftover_blocks = deque(leftover_blocks)

    while leftover_blocks:
        # start a new group with the largest remaining block (place it whole)
        largest_block = leftover_blocks.popleft()
        current_group = list(largest_block)
        space = group_size - len(current_group)

        
        while space > 0 and leftover_blocks:
            block = leftover_blocks.popleft()
            if len(block) <= space:
                # take entire block
                current_group.extend(block)
                space -= len(block)
                # continue to next block
            else:
                # take a chunk from this block to fill space, keep remainder as a block
                take = block[:space]
                remain = block[space:]
                current_group.extend(take)
               
                leftover_blocks.appendleft(remain)  
                space = 0

        groups.append(current_group)

    
    if len(groups) > n_groups:
        
        raise ValueError(f"Created {len(groups)} groups but expected {n_groups} (check input).")

    while len(groups) < n_groups:
        groups.append([])

    return groups


# --- Main app ---
def run():
    uploaded_file = st.file_uploader("Upload input_Make Groups.xlsx", type=["xlsx"])
    n_groups = st.number_input("Number of groups", min_value=2, max_value=100, value=DEFAULT_GROUPS, step=1)

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f" Could not read file: {e}")
            return

        # Ensure required cols
        for col in ["Roll","Name","Email"]:
            if col not in df.columns:
                df[col] = ""
        df["Branch"] = df["Roll"].apply(extract_branch)

        # --- Mixed strategy (your new logic) ---
        mixed_groups = mixed_strategy(df, n_groups)
        stats_mixed = make_stats(mixed_groups, n_groups)

        # --- Uniform strategy (optional comparison) ---
        uniform_groups = uniform_strategy(df, n_groups)
        stats_uniform = make_stats(uniform_groups, n_groups)

        # --- Metrics ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Students", f"{len(df)}")
        c2.metric("Groups", f"{n_groups}")
        c3.metric("Avg / Group", f"{(len(df)/n_groups):.2f}")
        c4.metric("Branches", f"{df['Branch'].nunique()}")

        st.subheader(" Stats - Mixed Strategy (Branch-wise RR per group)")
        st.dataframe(stats_mixed, use_container_width=True, hide_index=True)

        st.subheader(" Stats - Uniform Strategy")
        st.dataframe(stats_uniform, use_container_width=True, hide_index=True)

        # Preview groups
        with st.expander(" Preview Mixed Groups"):
            for gi, group_rows in enumerate(mixed_groups, start=1):
                st.markdown(f"*G{gi}*")
                gdf = pd.DataFrame(group_rows)
                st.dataframe(gdf[["Roll","Name","Email","Branch"]], use_container_width=True, hide_index=True)

        with st.expander(" Preview Uniform Groups"):
            for gi, group_rows in enumerate(uniform_groups, start=1):
                st.markdown(f"*G{gi}*")
                gdf = pd.DataFrame(group_rows)
                st.dataframe(gdf[["Roll","Name","Email","Branch"]], use_container_width=True, hide_index=True)

        # --- Download Excel ---
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

        st.download_button(
            label="⬇ Download output.xlsx",
            data=output,
            file_name="output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


run()
