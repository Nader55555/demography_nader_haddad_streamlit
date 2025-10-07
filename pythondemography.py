import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
import base64

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

# Family-size composition / Region sunburst
fig = px.sunburst(df, path=["Region", "Dominant size"],
                  title="Family Size Composition by Region",
                  color="Dominant size",
                  color_discrete_map={"1–3":"lightblue", "4–6":"orange", "7+":"red"},
                  labels={"Dominant size":"Dominant Family Size"})
st.plotly_chart(fig, use_container_width=True)

# st.write("The sunburst chart shows the dominant family size composition by region in Lebanon. It highlights the variations in family sizes across different regions.")

# st.markdown(
#     "<div class='note'>The sunburst chart shows the dominant family size "
#     "composition by region in Lebanon. It highlights the variations in family "
#     "sizes across different regions.</div>",
#     unsafe_allow_html=True
# )
st.markdown(
    "<div class='note'>
    The sunburst chart shows the dominant family size composition by region in Lebanon. "
    "It highlights the variations in family sizes across different regions.  \n\n"
    "**Insights:**  \n"
    "• **Dominant Family Size:** Across most regions in Lebanon, medium-sized families (4–6 members) are the most common household composition. "
    "This indicates a general cultural or economic trend favoring moderate family units, balancing between large traditional families and smaller modern ones.  \n"
    "• **Regional Differences:** North and South Governorates show the highest concentration of 4–6 member families, suggesting stable middle-sized households. "
    "Some regions show minor proportions of larger families (7+), possibly reflecting rural or traditional communities. "
    "Urban areas (like Beirut or Mount Lebanon) have more 1–3 member families, aligning with higher living costs and more single or small-family households.</div>",
    unsafe_allow_html=True
)



st.divider()



#add a box plot + points for the percentage of youth vs region with plotly express

Y15 = "Percentage of Youth - 15-24 years"

fig = px.box(
    df,
    x="Region",
    y=Y15,
    points="all",                 # show all towns as points
    hover_name="Town",            # big title on hover
    hover_data={                  # extra fields on hover
        "Region": True,
        Y15: ':.1f',              # format number
    }
)
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    "<div class='note'>The box plot illustrates the distribution of the percentage "
    "of youth (15–24 years) across different regions in Lebanon. It helps identify "
    "regions with higher or lower youth populations.</div>",
    unsafe_allow_html=True
)
st.divider()

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



