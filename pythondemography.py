import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
import base64

### adding css 
st.markdown("""
<style>
/* ===== Make filter widgets bigger & clearer ===== */

/* Card behind the whole filter block (optional) */
.filter-card {
  background: rgba(255,255,255,0.95);
  padding: 18px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  margin: 8px 0 14px 0;
}

/* Labels above widgets */
.stMultiSelect > label, .stSelectbox > label, .stSlider > label,
.stRadio > label, .stCheckbox > label { 
  font-size: 1.05rem; 
  font-weight: 700;
}

/* Multiselect input & tags */
.stMultiSelect div[data-baseweb="select"] { font-size: 1.05rem; }
.stMultiSelect div[data-baseweb="tag"] {
  font-size: 0.95rem;
  padding: 6px 10px;
  border-radius: 8px;
}

/* Radio as pill buttons */
.stRadio [role="radiogroup"] { gap: 12px; }
.stRadio label {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 6px 14px;
  font-weight: 700;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.stRadio input:checked + div {
  background: #f3f3f3 !important;
  border: 1px solid #111 !important;
}

/* Slider: thicker track + larger knob */
.stSlider div[data-baseweb="slider"] > div { height: 10px; }               /* track height */
.stSlider div[data-baseweb="slider"] div[role="slider"] {                   /* knob */
  width: 18px; height: 18px; border: 2px solid #d33; background: #fff;
}

/* Checkbox text a bit larger */
.stCheckbox p { font-size: 1.05rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


###


def thick_divider():
    st.markdown(
        "<hr style='border:3px solid black; margin:0 -1rem;'>",
        unsafe_allow_html=True
    )


st.markdown("""
<style>
.note {
  background: rgba(255,255,255,0.88);   /* light card over the photo */
  border-radius: 12px;
  padding: 12px 16px;
  margin: 8px 0 18px 0;                 /* <-- bottom space below the text */
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
  font-weight: 600;
}
.note p { margin: 0; line-height: 1.5; color: #222; font-size: 1.05rem; }
</style>
""", unsafe_allow_html=True)

def set_page_bg(img_path: str):
    """Set a full-page background image."""
    img_bytes = Path(img_path).read_bytes()
    b64 = base64.b64encode(img_bytes).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: 
              linear-gradient(rgba(255,255,255,0.30), rgba(255,255,255,0.30)),
              url("data:image/jpg;base64,{b64}") no-repeat center center fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

set_page_bg("getlstd-property-photo.jpg")




st.set_page_config(layout="wide")

left, center, right = st.columns([1, 2, 1])

with left:
    st.image(Path("Flag_of_Lebanon.svg"), use_container_width=True)

with center:
    st.markdown("""
    <style>
    .hero{
      background: rgba(255,255,255,0.85);
      border-radius: 16px; padding: 22px 26px; 
      box-shadow: 0 6px 20px rgba(0,0,0,.10);
    }
    .hero h1{ margin:0 0 6px 0; font-size: 2.2rem; color:#111; }
    .hero p{ margin:0; font-size: 1.05rem; color:#333; font-weight: 600; }
    </style>
    <div class="hero">
      <h1>Nader Haddad – Demographic Data Analysis</h1>
      <p>This app analyzes demographic data from Lebanon.</p>
    </div>
    """, unsafe_allow_html=True)
    # …your charts here…

with right:
    st.image(Path("Flag_of_Lebanon.svg"), use_container_width=True)




#add into df the demographic data from the csv file

df = pd.read_csv("demograph.csv")

df = df[df["Percentage of Youth - 15-24 years"] > 0]

# fix any trailing spaces in column names
df = df.rename(columns=lambda c: c.strip())

# short handles (match your file)
W   = "Percentage of Women"
M   = "Percentage of Men"
E65 = "Percentage of Eldelry - 65 or more years"
Y15 = "Percentage of Youth - 15-24 years"
F13 = "Average family size - 1 to 3 members"
F46 = "Average family size - 4 to 6 members"
F7p = "Average family size - 7 or more members"
TOWN = "Town"

# keep percentages in 0–100 just in case
for c in [W, M, E65, Y15]:
    df[c] = df[c].clip(0, 100)

# readable region label from the DBpedia URI
def region_label(u):
    s = str(u)
    return s.rsplit("/", 1)[-1].replace("_", " ") if s else s

df["Region"] = df["refArea"].map(region_label)

# make sure % columns are numeric & clipped
for c in [W, M, Y15, E65]:
    df[c] = pd.to_numeric(df[c], errors="coerce").clip(0, 100)

# helper columns
df["Gender gap (W - M)"] = df[W] - df[M]
df["Abs gender gap"] = df["Gender gap (W - M)"].abs()
df["Dominant size"] = df[[F13, F46, F7p]].idxmax(axis=1).map(
    {F13:"1–3", F46:"4–6", F7p:"7+"}
)
##############################################

# --- Interactive Family-size Composition / Region Sunburst ---

# --- Styling for labels
st.markdown("""
<style>
.label-box {
    background-color: white;
    padding: 8px 14px;
    border-radius: 6px;
    display: inline-block;
    font-size: 1.2rem;   /* makes text bigger */
    font-weight: 600;    /* semi-bold for readability */
    color: black;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# Region filter
st.markdown("<div class='label-box'>Select Regions</div>", unsafe_allow_html=True)
all_regions = sorted(df["Region"].dropna().unique().tolist())
selected_regions = st.multiselect(
    "",  # no label, we already added our own
    options=all_regions,
    default=all_regions
)

# Family size radio
# st.markdown("<div class='label-box'>Family Size View</div>", unsafe_allow_html=True)
size_choice = st.radio(
    "",
    ["All", "1-3", "4-6", "7+"],
    index=0,
    horizontal=True
)

# --- Filtered data ---
filtered_df = df[df["Region"].isin(selected_regions)].copy()
if size_choice != "All":
    filtered_df = filtered_df[
        filtered_df["Dominant size"].astype(str).str.replace("–", "-", regex=False).str.strip() == size_choice
    ]

# --- Color map and chart ---
color_map = {"1-3": "lightblue", "1–3": "lightblue",
             "4-6": "orange", "4–6": "orange",
             "7+": "red"}

if filtered_df.empty:
    st.info("No data available for this selection.")
else:
    fig = px.sunburst(
        filtered_df,
        path=["Region", "Dominant size"],
        title="Family Size Composition by Region",
        color="Dominant size",
        color_discrete_map=color_map,
        labels={"Dominant size": "Dominant Family Size"}
    )
    st.plotly_chart(fig, use_container_width=True)


##OLD PIE CHARM
# # Family-size composition / Region sunburst
# fig = px.sunburst(df, path=["Region", "Dominant size"],
#                   title="Family Size Composition by Region",
#                   color="Dominant size",
#                   color_discrete_map={"1–3":"lightblue", "4–6":"orange", "7+":"red"},
#                   labels={"Dominant size":"Dominant Family Size"})
# st.plotly_chart(fig, use_container_width=True)

# st.write("The sunburst chart shows the dominant family size composition by region in Lebanon. It highlights the variations in family sizes across different regions.")

# st.markdown(
#     "<div class='note'>The sunburst chart shows the dominant family size "
#     "composition by region in Lebanon. It highlights the variations in family "
#     "sizes across different regions.</div>",
#     unsafe_allow_html=True
# )
st.markdown(
    "<div class='note'>The sunburst chart shows the dominant family size composition by region in Lebanon. "
    "It highlights the variations in family sizes across different regions.  \n\n"
    "**Insights:**  \n"
    "• **Dominant Family Size:** Across most regions in Lebanon, medium-sized families (4–6 members) are the most common household composition. "
    "This indicates a general cultural or economic trend favoring moderate family units, balancing between large traditional families and smaller modern ones.  \n"
    "• **Regional Differences:** North and South Governorates show the highest concentration of 4–6 member families, suggesting stable middle-sized households. "
    "Some regions show minor proportions of larger families (7+), possibly reflecting rural or traditional communities. "
    "Urban areas (like Beirut or Mount Lebanon) have more 1–3 member families, aligning with higher living costs and more single or small-family households.</div>",
    unsafe_allow_html=True
)



thick_divider()
st.markdown("<div class='filter-card'>", unsafe_allow_html=True)
##############################################
# ---------- INTERACTIVE BOX PLOT (Percentage of Youth 15–24) ----------

Y15 = "Percentage of Youth - 15-24 years"

# 1) Controls
all_regions = sorted(df["Region"].dropna().unique().tolist())

# sel_regions = st.multiselect("Filter Regions", options=all_regions, default=all_regions)
sel_regions = st.multiselect("Filter Regions", options=all_regions, default=all_regions)

# Optional: town filter (depends on region selection)
available_towns = sorted(df[df["Region"].isin(sel_regions)]["Town"].dropna().unique().tolist())
sel_towns = st.multiselect("Filter Towns (optional)", options=available_towns, default=[])

# Y-range slider
min_y, max_y = float(df[Y15].min()), float(df[Y15].max())
y_range = st.slider(
    "Show values between",
    min_value=float(min_y), max_value=float(max_y),
    value=(float(min_y), float(max_y)),
    step=1.0
)

# Points & stats
points_mode = st.radio(
    "Points",
    ["All", "Outliers only", "None"],
    index=0,
    horizontal=True
)
boxmean_on = st.checkbox("Show mean in box", value=True)

points_kw = {"All": "all", "Outliers only": "outliers", "None": False}[points_mode]

# 2) Filter data
f = df[df["Region"].isin(sel_regions)].copy()
if sel_towns:
    f = f[f["Town"].isin(sel_towns)]
f = f[(f[Y15] >= y_range[0]) & (f[Y15] <= y_range[1])]

# 3) Build figure
if f.empty:
    st.info("No data for this selection.")
else:
    fig = px.box(
        f,
        x="Region",
        y=Y15,
        points=points_kw,
        hover_name="Town",
        hover_data={"Region": True, Y15: ':.1f'},
    )
    # mean marker
    fig.update_traces(boxmean=boxmean_on)

    # nicer hover + margins
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>%{x}<br>"+Y15+": %{y:.1f}%<extra></extra>")
    fig.update_layout(
        margin=dict(t=10, r=10, b=10, l=10),
        yaxis_title="Percentage of Youth (15–24 years)",
        xaxis_title="Region"
    )

    st.plotly_chart(fig, use_container_width=True)



##OLD CODE  OF BOX 
# #add a box plot + points for the percentage of youth vs region with plotly express

# Y15 = "Percentage of Youth - 15-24 years"

# fig = px.box(
#     df,
#     x="Region",
#     y=Y15,
#     points="all",                 # show all towns as points
#     hover_name="Town",            # big title on hover
#     hover_data={                  # extra fields on hover
#         "Region": True,
#         Y15: ':.1f',              # format number
#     }
# )
# st.plotly_chart(fig, use_container_width=True)

# st.markdown(
#     "<div class='note'>The box plot illustrates the distribution of the percentage "
#     "of youth (15–24 years) across different regions in Lebanon. It helps identify "
#     "regions with higher or lower youth populations.</div>",
#     unsafe_allow_html=True
# )

st.markdown(
    """
    <div class='note'>
    The box plot shows the percentage of youth (15–24 years old) in different regions of Lebanon.
    It helps compare which regions have more young people and how spread out their numbers are. <br><br>
    Insights:<br>
    • <b>Tripoli</b> and <b>Baalbek-Hermel</b> have some of the highest youth percentages, showing that these areas have a larger young population compared to others. <br>
    • Regions like <b>Mount Lebanon</b> and <b>Beirut</b> have more mixed values, meaning some parts have many young people while others have fewer.
    </div>
    """,
    unsafe_allow_html=True
)


thick_divider()

#add a box plot + points for the percentage of elderly vs region with plotly express
E65 = "Percentage of Eldelry - 65 or more years"
fig = px.box(
    df,
    x="Region",
    y=E65,
    points="all",                 # show all towns as points
    hover_name="Town",            # big title on hover
    hover_data={                  # extra fields on hover
        "Region": True,
        E65: ':.1f',              # format number
    }
)
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    "<div class='note'>The box plot illustrates the distribution of the "
    "percentage of elderly (65 or more years) across different regions in Lebanon. "
    "It helps identify regions with higher or lower elderly populations.</div>",
    unsafe_allow_html=True
)




































