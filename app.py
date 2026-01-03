import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="VitalLink 2.0",
    page_icon="🏥",
    layout="wide"
)

# =====================================================
# STYLES
# =====================================================
st.markdown("""
<style>
.big-font { font-size:20px; font-weight:600; }
.alert { color:red; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# DATA LOAD
# =====================================================
DATA_FILE = "hospital_inventory.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

df = load_data()

# =====================================================
# AUTO-FIX MISSING COLUMNS (NO CRASH GUARANTEE)
# =====================================================
required_columns = {
    "Daily_Usage": lambda n: np.random.randint(5, 20, n),
    "Supplier_Lead_Time": lambda n: np.random.randint(2, 10, n),
    "Cost_Per_Unit": lambda n: np.random.randint(50, 500, n),
    "Supplier_Name": lambda n: np.random.choice(
        ["MedSupply Co", "LifeLine Pharma", "HealthCorp"], n
    )
}

for col, generator in required_columns.items():
    if col not in df.columns:
        df[col] = generator(len(df))

# =====================================================
# FEATURE ENGINEERING
# =====================================================
df["Days_To_Stockout"] = (
    df["Quantity_Available"] / df["Daily_Usage"]
).replace([np.inf, -np.inf], 0).fillna(0)

# =====================================================
# ML MODEL – STOCKOUT PREDICTION
# =====================================================
X = df[
    ["Quantity_Available", "Minimum_Required",
     "Daily_Usage", "Supplier_Lead_Time"]
]
y = df["Days_To_Stockout"]

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)
model.fit(X, y)

df["Predicted_Stockout_Days"] = model.predict(X).round(1)

# =====================================================
# HEADER
# =====================================================
st.title("🏥 VitalLink 2.0 – AI Supply Chain Command")
st.markdown("**Live Monitoring • Predictive AI • Smart Procurement**")

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "🤖 AI Predictions",
    "🔁 Stock Transfer AI",
    "📝 Smart Procurement"
])

# =====================================================
# TAB 1 – DASHBOARD
# =====================================================
with tab1:
    critical = df[df["Quantity_Available"] < df["Minimum_Required"]]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Hospitals", df["Hospital_Name"].nunique())
    k2.metric("Total Stock", int(df["Quantity_Available"].sum()))
    k3.metric("Critical Items", len(critical))
    k4.metric(
        "Inventory Value",
        f"₹{int((df['Quantity_Available'] * df['Cost_Per_Unit']).sum()):,}"
    )

    if not critical.empty:
        st.toast("🚨 Critical stock detected!", icon="⚠️")

    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color=df["Quantity_Available"] < df["Minimum_Required"],
        size="Minimum_Required",
        hover_name="Hospital_Name",
        hover_data=["Item_Name", "Quantity_Available"],
        zoom=5
    )
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TAB 2 – AI STOCKOUT PREDICTION
# =====================================================
with tab2:
    st.subheader("🤖 AI Stock-Out Prediction")

    hospital = st.selectbox(
        "Hospital",
        df["Hospital_Name"].unique()
    )

    item = st.selectbox(
        "Item",
        df[df["Hospital_Name"] == hospital]["Item_Name"].unique()
    )

    record = df[
        (df["Hospital_Name"] == hospital) &
        (df["Item_Name"] == item)
    ].iloc[0]

    st.metric(
        "Predicted Days to Stock-Out",
        f"{record['Predicted_Stockout_Days']} days"
    )

    if record["Predicted_Stockout_Days"] < record["Supplier_Lead_Time"]:
        st.error("🚨 AI ALERT: Stock-out before supplier delivery!")

        st.markdown("### 🧠 AI Explanation")
        st.write(f"""
        • Daily usage: **{record['Daily_Usage']} units/day**  
        • Supplier lead time: **{record['Supplier_Lead_Time']} days**  
        • Current stock insufficient buffer  
        """)
    else:
        st.success("✅ Stock is safe based on AI prediction.")

# =====================================================
# TAB 3 – INTER-HOSPITAL TRANSFER AI
# =====================================================
with tab3:
    st.subheader("🔁 Inter-Hospital Stock Redistribution")

    needy = df[df["Quantity_Available"] < df["Minimum_Required"]]

    if needy.empty:
        st.success("No hospitals require emergency stock.")
    else:
        for _, row in needy.iterrows():
            donors = df[
                (df["Item_Name"] == row["Item_Name"]) &
                (df["Quantity_Available"] > row["Minimum_Required"] * 2)
            ]

            if not donors.empty:
                donor = donors.iloc[0]
                st.info(
                    f"Transfer **{row['Item_Name']}** "
                    f"from **{donor['Hospital_Name']}** "
                    f"to **{row['Hospital_Name']}**"
                )

# =====================================================
# TAB 4 – SMART PROCUREMENT
# =====================================================
with tab4:
    reorder = df[df["Quantity_Available"] < df["Minimum_Required"]]

    if reorder.empty:
        st.success("No procurement needed.")
    else:
        reorder = reorder.copy()
        reorder["Suggested_Order_Qty"] = (
            reorder["Minimum_Required"] * 3
            - reorder["Quantity_Available"]
        )

        st.dataframe(
            reorder[
                ["Hospital_Name", "Item_Name",
                 "Supplier_Name", "Suggested_Order_Qty"]
            ],
            use_container_width=True
        )

        po = "URGENT PURCHASE REQUEST\n\n"
        for _, r in reorder.iterrows():
            po += (
                f"- {r['Hospital_Name']} | "
                f"{r['Item_Name']} | "
                f"Qty: {int(r['Suggested_Order_Qty'])}\n"
            )

        st.text_area("Generated PO", po, height=200)

# =====================================================
# FOOTER
# =====================================================
st.caption("VitalLink 2.0 | AI For Good Hackathon 2025")
