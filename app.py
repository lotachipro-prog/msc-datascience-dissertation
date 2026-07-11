
Claude finished the response
[00:20:49] 🐍 Python dependencies were installed from /mount/src/msc-datascience-dissertation/requirements.txt using uv.
Check if streamlit is installed
Streamlit is already installed
[00:20:51] 📦 Processed dependencies!
2026-07-11 00:20:52.986 Uvicorn server started on :::8501

2026-07-11 00:21:01.722 Please replace use_container_width with width.

`use_container_width will be removed after 2025-12-31.`

For use_container_width=True, use width='stretch'. For use_container_width=False, use width='content'.
2026-07-11 00:21:01.769 Please replace use_container_width with width.

`use_container_width will be removed after 2025-12-31.`

For use_container_width=True, use width='stretch'. For use_container_width=False, use width='content'.
2026-07-11 00:21:01.779 Please replace use_container_width with width.

`use_container_width will be removed after 2025-12-31.`

For use_container_width=True, use width='stretch'. For use_container_width=False, use width='content'.
2026-07-11 00:21:05.845 Please replace use_container_width with width.

`use_container_width will be removed after 2025-12-31.`

For use_container_width=True, use width='stretch'. For use_container_width=False, use width='content'.
2026-07-11 00:21:05.856 Please replace use_container_width with width.

`use_container_width will be removed after 2025-12-31.`

For use_container_width=True, use width='stretch'. For use_container_width=False, use width='content'.
2026-07-11 00:21:05.862 Please replace use_container_width with width.

`use_container_width will be removed after 2025-12-31.`

For use_container_width=True, use width='stretch'. For use_container_width=False, use width='content'.
/app/scripts/run-streamlit.sh: line 9:   183 Segmentation fault      sudo -E -u appuser /home/adminuser/venv/bin/streamlit "$@"

Show more

Diagnosed numpy/pandas binary incompatibility causing segmentation fault
Diagnosed numpy/pandas binary incompatibility causing segmentation fault
Good — that log is decisive. Ignore all the use_container_width messages; those are harmless deprecation warnings, not the problem. The actual crash is the very last line:

Segmentation fault ... streamlit

A segmentation fault is a native-code crash — it isn't a bug in the app's Python logic (there's no traceback, no missing file, no missing module). The app actually installed, started, and rendered your charts successfully, then the underlying numeric libraries crashed at the C level. On Streamlit Cloud this almost always means numpy and pandas got installed at mismatched versions — uv grabbed bleeding-edge releases with incompatible binary interfaces, and they segfault when they talk to each other.

The fix is to pin the versions so they're a known-compatible set. I've made you a corrected requirements file:


Ran a command, read a file
Ran a command, read a file
Do this — it's a two-minute test that isolates the one variable:

In your repo, open requirements.txt, click the pencil (Edit), select all, delete, and paste in the pinned version above (or drag the downloaded file to overwrite). Commit.
Go to share.streamlit.io → your app → the three-dot menu → "Reboot app" — this forces a clean reinstall of the pinned versions rather than reusing the broken ones.
Watch the logs. The install step will take a bit longer this time because it's fetching specific versions. Then check the app in an incognito window.
The exact pins matter here: numpy 2.1.3 with pandas 2.2.3 is a combination with wide wheel coverage and no known ABI conflict, so uv can't substitute something incompatible. That's the difference from your current >= version file, which let it pull whatever was newest.

If it still segfaults after this — then the cause is the other Streamlit Cloud crash trigger, memory, and I have a lever ready: the app currently loads one CSV (esgsi_extended.csv) it never actually uses, and the PDF scanner pulls in some heavy native libraries. I can strip both out to cut the memory footprint hard. So if the reboot doesn't fix it, just tell me "still crashing" and roughly how big your CSV files are, and I'll send a slimmed app.py. But try the pin first — I'd put this at 80% to be the whole fix.


Requirements
TXT 

Oh no. Error running app. If you need help, try the Streamlit docs and forums. [     UTC     ] Logs for msc-datascience-dissertation-6bpmrkct8mmnuqfnyknrrl.streamlit.app/ ──────────────────────────────────────────────────────────────────────────────────────── [00:20:43] 🚀 Starting up repo

pasted


Diagnosed Python version incompatibility and architected deployment solution
Diagnosed Python version incompatibility and architected deployment solution
That log is the smoking gun, and it points at something neither of us could see until now: the very first line says Using Python 3.14.6. Streamlit deployed your app on Python 3.14, which is brand-new, and that single fact explains both failures you've hit:

First attempt (before my pins): it grabbed the newest packages — numpy 2.5.1, pandas 3.0.3 — which do have 3.14 wheels, so they installed, but they're so fresh they crash at runtime. That's your segmentation fault.
Second attempt (with my pins): the stable versions I specified don't have 3.14 wheels yet, so it tried to compile pillow and pandas from source, and the build died on a missing zlib — that's the wall of red text.
So on Python 3.14 you're stuck between "installs but segfaults" and "won't install." The fix isn't in the requirements file — it's the Python version. Move the app to Python 3.12 and the whole problem evaporates: every package you need has a stable, pre-built 3.12 wheel, so nothing compiles and nothing segfaults.

I've made one small robustness tweak to the requirements too — unpinning pdfplumber so it always pulls a version whose image library has a matching wheel:


Ran a command, read a file
Ran a command, read a file
The catch: Streamlit Cloud only lets you set the Python version when an app is first created, not afterward — so the reliable path is to delete this app and redeploy. That sounds heavier than it is (two minutes), and it comes with a bonus: I noticed from the log that your app is currently living on a random URL (msc-datascience-dissertation-6bpmrkct8mmnuqfnyknrrl.streamlit.app), not the clean address printed in your dissertation. Redeploying lets you fix both at once.

Here's the sequence:

Replace requirements.txt in the repo with the version above (pencil → select all → paste → commit).
Go to share.streamlit.io, find the app, click the ⋮ menu → Delete. (This also frees up the URL name.)
Click Create app → deploy from GitHub: repo lotachipro-prog/msc-datascience-dissertation, branch main, main file app.py.
Before hitting Deploy, open "Advanced settings" and set two things:
Python version → 3.12
App URL subdomain → lotachipro-prog-msc-datascience-dissertation (this restores the exact link in your dissertation's Appendix D).
Deploy.
How to confirm it worked: watch the new build log's first line — it should now read Using Python 3.12 instead of 3.14. The install step will list packages ending in Installed … packages with no compiling and no red text, and the app will open.

Two small things: if the dropdown doesn't offer 3.12 for some reason, pick 3.13 (the pinned versions have 3.13 wheels too). And if step 4 says the subdomain is unavailable, it means an older app is still holding that name — delete that one as well, then it'll be free. Once it's up, send me the screenshot and I'll confirm the matrix and leaderboard rendered correctly against your real data before you put it in front of anyone.


Requirements
TXT 

Error installing requirements. Click "Manage App" and consult the terminal for more details. If you still have questions, leave a message in our forums and we will get back to you ASAP. [     UTC     ] Logs for lotachipro-prog-msc-datascience-dissertation.streamlit.app/ ───────────────────

pasted

The URL is fixed — good — but look at the first line again: Using Python 3.14.6. The Python version didn't take. Either the advanced-settings dropdown wasn't set to 3.12, or the setting didn't stick when the app was recreated. Everything downstream is the same 3.14 problem repeating: pillow tries to compile from source, hits missing zlib, dies.

So rather than fight the platform's Python version again, let me remove the dependency that's actually breaking the build. Pillow is only being pulled in because of pdfplumber — the log says so explicitly. And pdfplumber only exists in your app to power the Live Report Scanner's PDF upload. Drop it, and the build has nothing left to compile: streamlit, pandas, numpy and plotly all ship pre-built wheels for every Python version including 3.14.

I'll swap the PDF parser for pypdf — pure Python, no C extensions, no pillow, no zlib:


Ran a command, read a file
Ran a command, read a file
Two files to replace, then it should build. Both are above.

What changed and why this ends it: the new requirements.txt has no pins at all — deliberately. Pinning was what forced pip to compile pandas and pillow from source on Python 3.14; unpinned, it just downloads whatever pre-built wheel matches the platform. And pdfplumber is gone, replaced by pypdf, which is pure Python — so pillow is no longer in your dependency tree at all. Pillow was the only package that needed compiling, and zlib was the only thing missing. Remove pillow, and there is nothing left for the build to fail on. The app itself works identically; I re-ran it end-to-end against test data after the swap.

Steps: replace requirements.txt and app.py in the repo (pencil → select all → paste, or drag-drop to overwrite), commit both, then Manage app → ⋮ → Reboot app.

Watch the log for one thing: the install section should now show Installed N packages with no Failed to download and build and no wall of copying src/PIL/... lines. That's your green light.

If you'd still rather be on 3.12 — and it is the healthier long-term setup — the way to force it independently of the deploy form is to commit a file named runtime.txt in the repo root containing the single line 3.12. Streamlit reads it at build time. But you don't need that to get running tonight; the dependency fix stands on its own.


Requirements
TXT 

App
PY 
1783782711203_image.png
It builds and runs — right URL, correct DOI, correct degree, correct label wording. Four bugs to kill, and all four are visible in that screenshot:

Leaderboard rows show a literal </div> and no status chip — Streamlit's markdown parser is choking on my multi-line HTML block. Needs to be emitted as one unbroken line.
Every row says CLEAN and green, even Shell 2021/2022 which are confirmed — the label column isn't being read, so status derivation falls through.
Matrix is empty — vague_per_1000 isn't resolving from your nlp_features.csv.
Threshold defaulted to 0.85 instead of 0.50, so "above threshold" reads 0.
Issues 2 and 3 are the same root cause: your real CSVs use column names my resolver doesn't recognise. Let me make the app tell us exactly what's in them, and harden it so it can't fail this way.


Ran a command, read a file
Ran a command, read a file
Replace app.py with this and reboot. What I changed:

The </div> leak and missing status chips — Streamlit's markdown parser was breaking my indented multi-line HTML into fragments. Rows are now emitted as a single unbroken HTML string, so the chip, score, risk bar and divergence chip will all render properly.

Everything showing CLEAN — the label column isn't resolving from your real CSV, so nothing could ever be marked Confirmed. I widened the resolver to accept the common variants (y_true, target, is_greenwashing, confirmed, gw_label, and others) and to read integer 1/0 as well as text.

The empty matrix — same root cause on vague_per_1000; I added many more name variants.

Threshold — back to 0.50 default (it had picked up a stale session value of 0.85, which is why "above threshold" read 0).

Bonus: company names now display as "Shell", "HSBC", "BP" rather than lowercase.

Now — the important part. Those extra name variants are educated guesses. To make this exact rather than probabilistic, after you redeploy, open the sidebar's new "Data diagnostics" expander. It prints the actual column names in each of your CSVs and shows which ones the app resolved. Screenshot that and send it to me, and I'll hard-map the real names in thirty seconds — no more guessing.

If the leaderboard still shows every row as CLEAN after this, that diagnostics panel is exactly what will tell us why: it'll show "label": null, and the CSV's real column name right beside it.


App
PY 






Claude is AI and can make mistakes. Please double-check responses.
App · PY
"""
FTSE ESG Anomaly Intelligence Platform
Cross-modal greenwashing detection for UK FTSE-listed firms.
 
MSc Data Science dissertation artefact - Lota Anene - University of Roehampton, 2026.
Anchor paper: V. Lagasio, "ESG-washing detection in corporate sustainability
reports," International Review of Financial Analysis, vol. 96, pt. B,
Art. no. 103742, 2024. doi: 10.1016/j.irfa.2024.103742
 
Reads pre-computed pipeline outputs (no transformer inference at request time):
  final_risk_scores_v3.csv, nlp_features.csv, ftse_naei_emissions.csv,
  esgsi_extended.csv, final_features.csv
Files are searched in ./, ./data/, ./data/processed/. Every section degrades
gracefully if a file or column is absent, so the app never hard-crashes.
"""
 
import re
from pathlib import Path
 
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
 
# ---------------------------------------------------------------- tokens ----
PAPER = "#FBFAF7"
CARD = "#FFFFFF"
INK = "#14212B"
SLATE = "#5B6B79"
RULE = "#E3E1DA"
NAVY = "#1F4E79"
RED = "#A4232B"      # confirmed
AMBER = "#9A6A00"    # flagged
GREEN = "#1E6B4F"    # clean
RED_BG = "#F7E9EA"
AMBER_BG = "#F5EEDC"
GREEN_BG = "#E7F0EC"
 
STATUS_STYLE = {
    "Confirmed": (RED, RED_BG),
    "Flagged": (AMBER, AMBER_BG),
    "Clean": (GREEN, GREEN_BG),
}
 
FONT_BODY = "'IBM Plex Sans', -apple-system, 'Segoe UI', sans-serif"
FONT_MONO = "'IBM Plex Mono', ui-monospace, 'SF Mono', Menlo, monospace"
 
# ------------------------------------------------------------- page setup ---
st.set_page_config(
    page_title="FTSE ESG Anomaly Intelligence Platform",
    page_icon=":bar_chart:",
    layout="wide",
)
 
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
 
html, body, [class*="css"], .stApp {{
  font-family: {FONT_BODY};
  color: {INK};
}}
.stApp {{ background: {PAPER}; }}
 
/* masthead */
.masthead {{ border-bottom: 2px solid {INK}; padding: 0 0 14px 0; margin-bottom: 4px; }}
.masthead h1 {{
  font-size: 1.45rem; font-weight: 700; letter-spacing: .01em; margin: 0; color: {INK};
}}
.masthead .sub {{ color: {SLATE}; font-size: .92rem; margin-top: 3px; }}
.masthead .prov {{
  color: {SLATE}; font-size: .78rem; text-align: right;
  font-family: {FONT_MONO}; line-height: 1.5;
}}
 
/* KPI cards */
.kpi {{
  background: {CARD}; border: 1px solid {RULE}; border-radius: 6px;
  padding: 14px 16px 12px 16px; height: 100%;
}}
.kpi .label {{
  font-size: .68rem; letter-spacing: .09em; text-transform: uppercase;
  color: {SLATE}; font-weight: 600;
}}
.kpi .value {{
  font-family: {FONT_MONO}; font-size: 1.9rem; font-weight: 600;
  color: {INK}; line-height: 1.15; margin-top: 2px;
}}
.kpi .note {{ font-size: .74rem; color: {SLATE}; margin-top: 2px; }}
 
/* leaderboard rows */
.lrow {{
  background: {CARD}; border: 1px solid {RULE}; border-radius: 6px;
  padding: 10px 12px; margin-bottom: 8px;
}}
.lrow .name {{ font-weight: 600; font-size: .93rem; }}
.lrow .yr {{ color: {SLATE}; font-family: {FONT_MONO}; font-size: .8rem; margin-left: 6px; }}
.lrow .score {{ font-family: {FONT_MONO}; font-size: .9rem; color: {INK}; }}
 
.chip {{
  display: inline-block; font-size: .68rem; font-weight: 600; letter-spacing: .05em;
  padding: 2px 8px; border-radius: 3px; text-transform: uppercase;
}}
 
/* divergence chip - the signature element */
.dchip {{
  font-family: {FONT_MONO}; font-size: .76rem; color: {SLATE};
  border-left: 3px solid {RULE}; padding-left: 8px; margin-top: 5px; display: inline-block;
}}
.dchip b {{ font-weight: 600; }}
.up {{ color: {RED}; }}
.down {{ color: {GREEN}; }}
.downbad {{ color: {RED}; }}
 
.riskbar {{ height: 4px; background: #EFEDE6; border-radius: 2px; margin-top: 7px; }}
.riskbar > div {{ height: 4px; border-radius: 2px; }}
 
section[data-testid="stSidebar"] {{
  background: #F3F1EB; border-right: 1px solid {RULE};
}}
.side-h {{
  font-size: .7rem; letter-spacing: .1em; text-transform: uppercase;
  color: {SLATE}; font-weight: 700; margin: 6px 0 2px 0;
}}
.cite {{
  background: {CARD}; border: 1px solid {RULE}; border-radius: 6px;
  padding: 10px 12px; font-size: .78rem; line-height: 1.45; color: {INK};
}}
.cite .doi {{ font-family: {FONT_MONO}; font-size: .72rem; color: {NAVY}; }}
 
.footnote {{ color: {SLATE}; font-size: .76rem; border-top: 1px solid {RULE};
             padding-top: 10px; margin-top: 22px; line-height: 1.5; }}
 
div[data-testid="stMetric"] {{ background: {CARD}; border: 1px solid {RULE};
  border-radius: 6px; padding: 10px 14px; }}
</style>
""",
    unsafe_allow_html=True,
)
 
# ------------------------------------------------------------- data layer ---
SEARCH_DIRS = [Path("."), Path("data"), Path("data/processed"), Path("data/raw")]
 
 
@st.cache_data(show_spinner=False)
def load_csv(name: str):
    for d in SEARCH_DIRS:
        p = d / name
        if p.exists():
            try:
                return pd.read_csv(p)
            except Exception:
                return None
    return None
 
 
def col(df: pd.DataFrame, *candidates):
    """Return the first column whose normalised name matches a candidate."""
    if df is None:
        return None
    norm = {re.sub(r"[^a-z0-9]", "", c.lower()): c for c in df.columns}
    for cand in candidates:
        key = re.sub(r"[^a-z0-9]", "", cand.lower())
        if key in norm:
            return norm[key]
    return None
 
 
def norm_company(s):
    s = str(s).upper().strip()
    s = re.sub(r"\b(PLC|GROUP|HOLDINGS|LTD|LIMITED|UK)\b", "", s)
    return re.sub(r"[^A-Z0-9]", "", s)
 
 
def derive_status(row, risk_c, label_c, thresh):
    if label_c is not None:
        raw = str(row.get(label_c, "")).strip().upper()
        if raw in {"1", "1.0", "TRUE", "CONFIRMED", "YES", "Y", "POSITIVE"}:
            return "Confirmed"
        if raw in {"FLAGGED", "ELEVATED", "HIGH RISK", "HIGH"}:
            return "Flagged"
    r = row.get(risk_c, np.nan) if risk_c else np.nan
    if pd.notna(r) and float(r) >= thresh:
        return "Flagged"
    return "Clean"
 
 
risk_df = load_csv("final_risk_scores_v3.csv")
nlp_df = load_csv("nlp_features.csv")
emis_df = load_csv("ftse_naei_emissions.csv")
esgsi_df = load_csv("esgsi_extended.csv")
 
# resolve the master frame
master = None
if risk_df is not None:
    master = risk_df.copy()
    C_COMP = col(master, "company", "firm", "name")
    C_YEAR = col(master, "year", "report_year")
    C_RISK = col(master, "risk_score", "final_risk", "probability", "prob", "score",
                 "risk", "oof_prob", "y_prob", "pred_prob", "predicted_prob")
    C_LABEL = col(master, "greenwashing_label", "label", "status", "known_status",
                  "is_greenwashing", "confirmed", "y", "y_true", "target", "gw_label",
                  "ground_truth", "actual")
else:
    C_COMP = C_YEAR = C_RISK = C_LABEL = None
 
# attach NLP features
C_VAGUE = C_SPEC = C_POS = None
if master is not None and nlp_df is not None:
    n_comp = col(nlp_df, "company", "firm", "name")
    n_year = col(nlp_df, "year", "report_year")
    if n_comp and n_year:
        nlp = nlp_df.copy()
        nlp["_k"] = nlp[n_comp].map(norm_company).astype(str) + "|" + nlp[n_year].astype(str)
        master["_k"] = master[C_COMP].map(norm_company).astype(str) + "|" + master[C_YEAR].astype(str)
        keep = [c for c in nlp.columns if c not in (n_comp, n_year, "_k")]
        master = master.merge(nlp[keep + ["_k"]].drop_duplicates("_k"), on="_k", how="left")
    C_VAGUE = col(master, "vague_per_1000", "vague_density", "vagueper1000",
                  "vague_commitment_per_1000", "vague", "vague_count_per_1000",
                  "vague_per1000", "vaguecommitment")
    C_SPEC = col(master, "specificity_ratio", "spec_ratio", "r_spec", "specificity",
                 "quant_specificity", "specificity_score")
    C_POS = col(master, "positive_per_1000", "positive_density", "positive",
                "positive_per1000", "sentiment_positive")
 
# attach emissions + YoY
C_CO2YOY = None
if master is not None and emis_df is not None:
    e_comp = col(emis_df, "ftse_company", "company", "operator")
    e_year = col(emis_df, "year")
    e_co2 = col(emis_df, "co2_tonnes", "co2", "emissions_tonnes", "co2tonnes")
    if e_comp and e_year and e_co2:
        e = emis_df[[e_comp, e_year, e_co2]].copy()
        e.columns = ["_ec", "_ey", "_co2"]
        e = e.sort_values(["_ec", "_ey"])
        e["_yoy"] = e.groupby("_ec")["_co2"].pct_change(fill_method=None) * 100
        e["_k"] = e["_ec"].map(norm_company).astype(str) + "|" + e["_ey"].astype(str)
        master = master.merge(e[["_k", "_co2", "_yoy"]].drop_duplicates("_k"), on="_k", how="left")
        C_CO2YOY = "_yoy"
 
# ---------------------------------------------------------------- sidebar ---
with st.sidebar:
    st.markdown('<div class="side-h">Filters</div>', unsafe_allow_html=True)
    if master is not None and C_YEAR:
        yrs = sorted(pd.to_numeric(master[C_YEAR], errors="coerce").dropna().astype(int).unique())
        y_lo, y_hi = (min(yrs), max(yrs)) if yrs else (2019, 2025)
        year_range = st.slider("Reporting year", y_lo, y_hi, (y_lo, y_hi))
    else:
        year_range = (2019, 2025)
    thresh = st.slider("Flag threshold (risk score)", 0.0, 1.0, 0.50, 0.05,
                       key="thresh_slider")
 
    st.markdown('<div class="side-h">Anchor paper</div>', unsafe_allow_html=True)
    st.markdown(
        """<div class="cite">V. Lagasio, &ldquo;ESG-washing detection in corporate
        sustainability reports,&rdquo; <i>International Review of Financial
        Analysis</i>, vol.&nbsp;96, pt.&nbsp;B, Art.&nbsp;no.&nbsp;103742, 2024.<br>
        <span class="doi">doi: 10.1016/j.irfa.2024.103742</span></div>""",
        unsafe_allow_html=True,
    )
 
    st.markdown('<div class="side-h">Model</div>', unsafe_allow_html=True)
    st.markdown(
        """<div class="cite">Logistic regression, leak-free Leave-One-Out CV.<br>
        <span style="font-family:'IBM Plex Mono',monospace">AUC 0.881 &middot;
        Recall 0.800 &middot; F1 0.615</span><br>
        37 company-year observations &middot; 11 firms &middot; 5 confirmed labels.<br>
        Label-permutation test: p = 0.009.</div>""",
        unsafe_allow_html=True,
    )
 
    with st.expander("Data diagnostics"):
        st.caption("Column resolution across loaded result files.")
        st.write({
            "final_risk_scores_v3.csv": list(risk_df.columns) if risk_df is not None else "NOT FOUND",
            "nlp_features.csv": list(nlp_df.columns) if nlp_df is not None else "NOT FOUND",
            "ftse_naei_emissions.csv": list(emis_df.columns) if emis_df is not None else "NOT FOUND",
        })
        st.write({"resolved": {"company": C_COMP, "year": C_YEAR, "risk": C_RISK,
                               "label": C_LABEL, "vague": C_VAGUE, "specificity": C_SPEC,
                               "co2_yoy": C_CO2YOY}})
 
    with st.expander("How scores are calculated"):
        st.markdown(
            "Reports are scored on rule-based disclosure features (vague, "
            "commitment, hedging and quantitative-specificity language) combined "
            "with ClimateBERT semantic embeddings, benchmarked against verified "
            "Scope 1 emissions from the UK National Atmospheric Emissions "
            "Inventory. Positive labels derive from ASA rulings (HSBC, Shell) "
            "and FCA/NGO scrutiny (BP 2023). All figures shown are computed "
            "offline by the dissertation pipeline; this dashboard reads the "
            "published result files."
        )
 
# --------------------------------------------------------------- masthead ---
mh_l, mh_r = st.columns([0.72, 0.28])
with mh_l:
    st.markdown(
        """<div class="masthead"><h1>FTSE ESG Anomaly Intelligence Platform</h1>
        <div class="sub">Cross-modal greenwashing detection &middot; UK FTSE
        &middot; 2019&ndash;2025 &middot; ClimateBERT + NAEI verified emissions</div>
        </div>""",
        unsafe_allow_html=True,
    )
with mh_r:
    st.markdown(
        """<div class="masthead"><div class="prov">Lota Anene<br>
        MSc Data Science &middot; University of Roehampton &middot; 2026</div></div>""",
        unsafe_allow_html=True,
    )
 
if master is None:
    st.error(
        "Result file `final_risk_scores_v3.csv` was not found in the repository "
        "(searched ./, data/, data/processed/). Commit the pipeline outputs and reboot the app."
    )
    st.stop()
 
# filtered view
view = master.copy()
view["_yearnum"] = pd.to_numeric(view[C_YEAR], errors="coerce")
view = view[(view["_yearnum"] >= year_range[0]) & (view["_yearnum"] <= year_range[1])]
view["_status"] = view.apply(lambda r: derive_status(r, C_RISK, C_LABEL, thresh), axis=1)
view[C_COMP] = view[C_COMP].astype(str).str.strip().str.title()
view[C_COMP] = view[C_COMP].str.replace(r"\bPlc\b", "plc", regex=True)
view[C_COMP] = view[C_COMP].str.replace(r"\bHsbc\b", "HSBC", regex=True)
view[C_COMP] = view[C_COMP].str.replace(r"\bSse\b", "SSE", regex=True)
view[C_COMP] = view[C_COMP].str.replace(r"\bBp\b", "BP", regex=True)
view["_risk"] = pd.to_numeric(view[C_RISK], errors="coerce") if C_RISK else np.nan
 
# ------------------------------------------------------------------- tabs ---
tab_matrix, tab_profile, tab_scan = st.tabs(
    ["Market anomaly matrix", "Company profiler", "Live report scanner"]
)
 
# =================================================================== TAB 1 ===
with tab_matrix:
    n_obs = len(view)
    n_firms = view[C_COMP].nunique()
    n_flag = int((view["_risk"] >= thresh).sum()) if C_RISK else 0
    n_conf = int((view["_status"] == "Confirmed").sum())
    avg_risk = float(view["_risk"].mean()) if C_RISK else float("nan")
 
    k1, k2, k3, k4 = st.columns(4)
    for c, label, value, note in (
        (k1, "Reports scanned", f"{n_obs}", f"{n_firms} unique firms"),
        (k2, "Above threshold", f"{n_flag}", f"risk score \u2265 {thresh:.2f}"),
        (k3, "Confirmed labels", f"{n_conf}", "ASA rulings \u00b7 FCA/NGO scrutiny"),
        (k4, "Mean risk score", f"{avg_risk:.3f}" if avg_risk == avg_risk else "\u2014", "market baseline"),
    ):
        c.markdown(
            f'<div class="kpi"><div class="label">{label}</div>'
            f'<div class="value">{value}</div><div class="note">{note}</div></div>',
            unsafe_allow_html=True,
        )
 
    st.markdown("")
    left, right = st.columns([0.62, 0.38], gap="large")
 
    # ---- cross-modal risk matrix -------------------------------------------
    with left:
        st.markdown("##### Cross-modal risk matrix")
        if C_CO2YOY and C_VAGUE:
            pts = view.dropna(subset=[C_CO2YOY, C_VAGUE]).copy()
            fig = go.Figure()
            x_max = max(20.0, float(pts[C_CO2YOY].max()) * 1.08) if len(pts) else 120
            y_max = max(1.0, float(pts[C_VAGUE].max()) * 1.15) if len(pts) else 3
            # divergence zone: emissions rising
            fig.add_shape(
                type="rect", x0=0, x1=x_max, y0=0, y1=y_max, layer="below",
                fillcolor="rgba(164,35,43,0.045)", line_width=0,
            )
            fig.add_annotation(
                x=x_max * 0.98, y=y_max * 0.97, text="EMISSIONS RISING",
                showarrow=False, xanchor="right",
                font=dict(family=FONT_MONO, size=10, color=RED),
            )
            for status, (fg, _bg) in STATUS_STYLE.items():
                sub = pts[pts["_status"] == status]
                if sub.empty:
                    continue
                fig.add_trace(go.Scatter(
                    x=sub[C_CO2YOY], y=sub[C_VAGUE], mode="markers",
                    name=status,
                    marker=dict(
                        size=(sub["_risk"].fillna(0.3) * 26 + 7),
                        color=fg, opacity=0.85,
                        line=dict(width=1, color=PAPER),
                    ),
                    customdata=np.stack([sub[C_COMP], sub[C_YEAR], sub["_risk"].round(3)], axis=-1),
                    hovertemplate="<b>%{customdata[0]}</b> %{customdata[1]}"
                                  "<br>CO\u2082 YoY: %{x:.1f}%"
                                  "<br>Vague / 1,000 words: %{y:.2f}"
                                  "<br>Risk score: %{customdata[2]}<extra></extra>",
                ))
            fig.update_layout(
                paper_bgcolor=PAPER, plot_bgcolor=CARD,
                font=dict(family=FONT_BODY, color=INK, size=12),
                xaxis=dict(title="Verified Scope 1 emissions, year-on-year change (%)",
                           gridcolor=RULE, zerolinecolor=SLATE, zerolinewidth=1),
                yaxis=dict(title="Vague commitment language (per 1,000 words)",
                           gridcolor=RULE, zeroline=False),
                legend=dict(orientation="h", y=1.08, x=0,
                            font=dict(size=11)),
                margin=dict(l=10, r=10, t=30, b=10), height=430,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                "Marker size scales with model risk score. The shaded region marks "
                "rising verified emissions; the greenwashing signature is high vague "
                "language inside this region."
            )
        else:
            missing = "ftse_naei_emissions.csv" if not C_CO2YOY else "nlp_features.csv (vague_per_1000)"
            st.info(f"Matrix unavailable: could not resolve data from `{missing}`.")
 
    # ---- risk leaderboard ---------------------------------------------------
    with right:
        st.markdown("##### Risk leaderboard")
        board = view.sort_values("_risk", ascending=False).head(10)
        for _, r in board.iterrows():
            status = r["_status"]
            fg, bg = STATUS_STYLE[status]
            risk = r["_risk"]
            bar = min(max(float(risk) if pd.notna(risk) else 0, 0), 1) * 100
            dchip = ""
            if C_CO2YOY and pd.notna(r.get(C_CO2YOY)) and C_SPEC and pd.notna(r.get(C_SPEC)):
                co2 = float(r[C_CO2YOY])
                co2_cls = "up" if co2 > 0 else "down"
                co2_arrow = "\u25b2" if co2 > 0 else "\u25bc"
                dchip = (f'<div class="dchip">CO\u2082 <b class="{co2_cls}">{co2_arrow} {co2:+.1f}%</b>'
                         f' &nbsp;\u00b7&nbsp; Spec <b>{float(r[C_SPEC]):.3f}</b></div>')
            html = (
                f'<div class="lrow">'
                f'<div style="display:flex;justify-content:space-between;align-items:baseline">'
                f'<span><span class="name">{r[C_COMP]}</span>'
                f'<span class="yr">{r[C_YEAR]}</span></span>'
                f'<span class="chip" style="color:{fg};background:{bg}">{status}</span>'
                f'</div>'
                f'<span class="score">{risk:.3f}</span>'
                f'<div class="riskbar"><div style="width:{bar:.0f}%;background:{fg}"></div></div>'
                f'{dchip}'
                f'</div>'
            )
            st.markdown(html, unsafe_allow_html=True)
 
# =================================================================== TAB 2 ===
with tab_profile:
    companies = sorted(view[C_COMP].dropna().unique())
    sel = st.selectbox("Company", companies)
    cdf = view[view[C_COMP] == sel].sort_values("_yearnum")
 
    p1, p2 = st.columns([0.55, 0.45], gap="large")
    with p1:
        st.markdown(f"##### {sel} — risk trajectory")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cdf[C_YEAR], y=cdf["_risk"], mode="lines+markers",
            line=dict(color=NAVY, width=2),
            marker=dict(size=9, color=[STATUS_STYLE[s][0] for s in cdf["_status"]]),
            hovertemplate="%{x}: %{y:.3f}<extra></extra>",
        ))
        fig.add_hline(y=thresh, line_dash="dot", line_color=SLATE,
                      annotation_text=f"threshold {thresh:.2f}",
                      annotation_font=dict(family=FONT_MONO, size=10, color=SLATE))
        fig.update_layout(
            paper_bgcolor=PAPER, plot_bgcolor=CARD,
            font=dict(family=FONT_BODY, color=INK, size=12),
            xaxis=dict(gridcolor=RULE, dtick=1), yaxis=dict(gridcolor=RULE, range=[0, 1]),
            margin=dict(l=10, r=10, t=10, b=10), height=320, showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
 
    with p2:
        st.markdown("##### Verified emissions (NAEI)")
        if C_CO2YOY and "_co2" in cdf.columns and cdf["_co2"].notna().any():
            fig = go.Figure(go.Bar(
                x=cdf[C_YEAR], y=cdf["_co2"], marker_color=NAVY, opacity=0.85,
                hovertemplate="%{x}: %{y:,.0f} t CO\u2082<extra></extra>",
            ))
            fig.update_layout(
                paper_bgcolor=PAPER, plot_bgcolor=CARD,
                font=dict(family=FONT_BODY, color=INK, size=12),
                xaxis=dict(gridcolor=RULE, dtick=1),
                yaxis=dict(gridcolor=RULE, title="tonnes CO\u2082"),
                margin=dict(l=10, r=10, t=10, b=10), height=320,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(
                "No matched NAEI operator for this company in the study's "
                "extraction — text-only evidence applies (see dissertation "
                "Section 3.3 on coverage limits)."
            )
 
    st.markdown("##### Report-year detail")
    detail_cols = [c for c in [C_YEAR, C_RISK, C_VAGUE, C_POS, C_SPEC, C_CO2YOY] if c]
    tbl = cdf[detail_cols + ["_status"]].rename(columns={
        C_YEAR: "Year", C_RISK: "Risk score", C_VAGUE: "Vague /1k",
        C_POS: "Positive /1k", C_SPEC: "Specificity", C_CO2YOY: "CO2 YoY %",
        "_status": "Status",
    })
    st.dataframe(tbl.round(3), use_container_width=True, hide_index=True)
 
# =================================================================== TAB 3 ===
with tab_scan:
    st.markdown("##### Scan a sustainability report")
    st.caption(
        "Upload a PDF to extract the rule-based disclosure features and compare "
        "them against the FTSE study distribution. This live scan uses the "
        "dissertation's lexicon features (Table 2 subset); full ClimateBERT "
        "semantic scoring runs in the offline pipeline, not in this browser demo."
    )
    up = st.file_uploader("Sustainability report (PDF, \u2264 25 MB)", type=["pdf"])
    if up is not None:
        try:
            from pypdf import PdfReader
            reader = PdfReader(up)
            text = " ".join((page.extract_text() or "") for page in reader.pages)
        except Exception as exc:
            st.error(f"Could not read that PDF ({exc}).")
            text = ""
 
        words = re.findall(r"[a-zA-Z']+", text.lower())
        n_words = max(len(words), 1)
        if n_words < 300:
            st.warning("Very little text extracted — the PDF may be image-only (scanned).")
        else:
            VAGUE = {"aim", "aspire", "ambition", "strive", "seek", "intend",
                     "endeavour", "explore", "commitment", "committed", "journey",
                     "roadmap", "pathway", "aspiration", "believe", "hope"}
            POSITIVE = {"sustainable", "green", "renewable", "responsible",
                        "resilient", "leading", "progress", "achievement",
                        "improved", "success", "positive", "strong"}
            v = sum(w in VAGUE for w in words) / n_words * 1000
            p = sum(w in POSITIVE for w in words) / n_words * 1000
            quant = len(re.findall(
                r"\b\d[\d,.]*\s*(?:%|percent|tonnes?|tco2e?|mwh|gwh|kt|mt)\b",
                text.lower()))
            sust_mentions = max(sum(w in {"sustainability", "sustainable", "esg",
                                          "climate", "emissions", "carbon"}
                                    for w in words), 1)
            spec = quant / sust_mentions
 
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Words extracted", f"{n_words:,}")
            c2.metric("Vague / 1,000", f"{v:.2f}")
            c3.metric("Positive / 1,000", f"{p:.2f}")
            c4.metric("Specificity ratio", f"{spec:.3f}")
 
            if C_VAGUE and view[C_VAGUE].notna().sum() >= 5:
                pct = float((view[C_VAGUE] < v).mean() * 100)
                st.markdown(
                    f"Vague-language density sits at the **{pct:.0f}th percentile** "
                    f"of the FTSE study distribution "
                    f"({'above' if pct >= 50 else 'below'} the median report)."
                )
            st.caption(
                "Indicative screening only: lexicon subset, no semantic model, "
                "no emissions cross-reference for uploaded documents."
            )
 
# ---------------------------------------------------------------- footer ----
st.markdown(
    """<div class="footnote">
    Scores are research risk indicators derived from public data (company
    sustainability reports; UK National Atmospheric Emissions Inventory, DESNZ).
    They are not allegations, findings, or regulatory determinations.
    Confirmed labels reflect ASA rulings (HSBC 2021&ndash;22, Shell 2021&ndash;22)
    and FCA/NGO scrutiny (BP 2023). Methodology, limitations and full results:
    dissertation Chapters 3&ndash;4 &middot;
    <a href="https://github.com/lotachipro-prog/msc-datascience-dissertation">source
    repository</a>.</div>""",
    unsafe_allow_html=True,
)
 








