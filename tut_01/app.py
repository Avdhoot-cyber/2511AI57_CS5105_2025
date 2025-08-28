import streamlit as st
import pandas as pd
import numpy as np
import os, io, zipfile, requests, base64, json
from pathlib import Path

# ---------------------------
# Utility Functions
# ---------------------------
def detect_branch(roll):
    """Infer branch from roll number string."""
    if isinstance(roll, str):
        return roll[:2].upper()
    return "NA"

def summarize(groups):
    """Return stats dataframe from grouped dict."""
    stats = []
    for g_id, members in groups.items():
        branches = [m['Branch'] for m in members]
        stats.append({
            "Group": g_id,
            "Size": len(members),
            "Branches": ", ".join(sorted(set(branches)))
        })
    return pd.DataFrame(stats)

# ---------------------------
# Grouping Strategies
# ---------------------------
def distribute_round_robin(df, n_groups):
    """Distribute students branch-wise in round robin fashion."""
    groups = {i: [] for i in range(1, n_groups + 1)}
    pointer = 1
    for branch, subset in df.groupby("Branch"):
        for _, row in subset.iterrows():
            groups[pointer].append(row.to_dict())
            pointer = 1 if pointer == n_groups else pointer + 1
    return groups

def balanced_grouping(df, n_groups):
    """Keep branch clusters together, then distribute leftovers."""
    groups = {i: [] for i in range(1, n_groups + 1)}
    sizes = [0] * n_groups

    # Assign branch blocks
    for branch, subset in df.groupby("Branch"):
        idx = np.argmin(sizes)
        groups[idx + 1].extend(subset.to_dict("records"))
        sizes[idx] += len(subset)

    # Balance by moving extras if needed
    flat = [r for recs in groups.values() for r in recs]
    np.random.shuffle(flat)
    groups = {i: [] for i in range(1, n_groups + 1)}
    for i, record in enumerate(flat):
        groups[(i % n_groups) + 1].append(record)
    return groups

# ---------------------------
# File / GitHub Export
# ---------------------------
def generate_excel(groups):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for g_id, members in groups.items():
            pd.DataFrame(members).to_excel(writer, sheet_name=f"Group_{g_id}", index=False)
    buf.seek(0)
    return buf

def generate_zip(groups):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for g_id, members in groups.items():
            content = pd.DataFrame(members).to_csv(index=False)
            zf.writestr(f"Group_{g_id}.csv", content)
    buf.seek(0)
    return buf

def push_to_github(token, repo, path, content, msg):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    data = {
        "message": msg,
        "content": base64.b64encode(content).decode("utf-8")
    }
    return requests.put(url, headers=headers, data=json.dumps(data))

# ---------------------------
# Streamlit App
# ---------------------------
def run():
    st.title("🤝 Student Grouping Tool")
    st.write("Upload student list, choose grouping strategy, and export results.")

    uploaded = st.file_uploader("Upload CSV (must contain Roll No, Name, Email)", type="csv")
    if not uploaded:
        return

    df = pd.read_csv(uploaded)
    if not set(["Roll No", "Name", "Email"]).issubset(df.columns):
        st.error("CSV missing required columns!")
        return

    df["Branch"] = df["Roll No"].apply(detect_branch)
    n_groups = st.number_input("How many groups?", min_value=2, max_value=20, value=4)
    method = st.radio("Choose grouping strategy:", ["Round Robin", "Balanced"])

    if st.button("Generate Groups"):
        groups = distribute_round_robin(df, n_groups) if method == "Round Robin" else balanced_grouping(df, n_groups)
        st.subheader("📊 Group Statistics")
        st.dataframe(summarize(groups))

        # Excel download
        excel_buf = generate_excel(groups)
        st.download_button("Download Excel", data=excel_buf, file_name="groups.xlsx")

        # Zip download
        zip_buf = generate_zip(groups)
        st.download_button("Download ZIP (CSVs)", data=zip_buf, file_name="groups.zip")

        # Optional GitHub push
        st.markdown("---")
        st.subheader("🚀 Push to GitHub")
        token = st.text_input("GitHub Token", type="password")
        repo = st.text_input("Repo (e.g. user/repo)")
        path = st.text_input("Target Path (e.g. groups/groups.xlsx)")
        if st.button("Upload to GitHub"):
            if token and repo and path:
                response = push_to_github(token, repo, path, excel_buf.getvalue(), "Add groups file")
                if response.status_code in [200, 201]:
                    st.success("Uploaded successfully!")
                else:
                    st.error(f"Upload failed: {response.json()}")
            else:
                st.warning("Fill all fields before uploading.")

if __name__ == "__main__":
    run()
