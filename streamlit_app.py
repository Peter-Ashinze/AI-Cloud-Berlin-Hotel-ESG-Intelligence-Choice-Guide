import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(
    page_title="Berlin Hotel ESG Intelligence Dashboard",
    page_icon="🌍",
    layout="wide"
)

API_URL = "https://berlin-hotel-esg-intelligence-fastapi.onrender.com"


@st.cache_data
def load_hotels():
    
if df.empty:
    st.error("No hotel data loaded from the backend API. Please refresh the app or wait for the Render backend to wake up.")
    st.stop()
    
    try:

        response = requests.get(
            f"{API_URL}/hotels",
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        return pd.DataFrame(data)

    except Exception as e:

        st.error(
            f"Backend API error: {e}"
        )

        return pd.DataFrame()

#@st.cache_data
#def load_hotels():
    #return pd.read_csv("berlin_hotels_advanced_ai_trust.csv")

df = load_hotels()

st.title(" Berlin Hotel ESG Intelligence Dashboard")
st.write(
    "AI-powered geospatial ESG, carbon, trust-risk and hotel recommendation dashboard for Berlin hotels."
)

st.divider()

# KPI cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Hotels", len(df))
col2.metric("Average ESG Score", round(df["esg_score"].mean(), 2))
col3.metric("Average Confidence", round(df["confidence_score"].mean(), 2))
col4.metric("Top Hotel", df.sort_values("trusted_recommendation_score", ascending=False).iloc[0]["name"])

st.divider()

# Sidebar filters
st.sidebar.header("Filters")

zones = ["All"] + sorted(df["berlin_zone"].dropna().unique().tolist())
selected_zone = st.sidebar.selectbox("Berlin Zone", zones)

risks = ["All"] + sorted(df["final_ai_trust_risk"].dropna().unique().tolist())
selected_risk = st.sidebar.selectbox("AI Trust Risk", risks)

filtered_df = df.copy()

if selected_zone != "All":
    filtered_df = filtered_df[filtered_df["berlin_zone"] == selected_zone]

if selected_risk != "All":
    filtered_df = filtered_df[filtered_df["final_ai_trust_risk"] == selected_risk]

# Table
st.subheader("Hotel ESG Summary")
st.dataframe(filtered_df, use_container_width=True)

st.divider()

# Top hotels
st.subheader("Top Recommended Hotels")

top_hotels = filtered_df.sort_values(
    "trusted_recommendation_score",
    ascending=False
).head(10)

st.dataframe(top_hotels, use_container_width=True)

fig_top = px.bar(
    top_hotels,
    x="name",
    y="trusted_recommendation_score",
    color="final_ai_trust_risk",
    title="Top Hotels by Trusted Recommendation Score"
)

st.plotly_chart(fig_top, use_container_width=True)

st.divider()

#Top ESG Performance Hotels in Berlin Zones

st.subheader(" Top 5 Hotels in Each Berlin Zone")

top5_by_zone = (
    filtered_df
    .sort_values(
        by=["berlin_zone", "trusted_recommendation_score"],
        ascending=[True, False]
    )
    .groupby("berlin_zone")
    .head(5)
)

st.dataframe(
    top5_by_zone[[
        "name",
        "berlin_zone",
        "hotel_class",
        "esg_score",
        "esg_class",
        "trusted_recommendation_score",
        "trusted_rank",
        "final_ai_trust_risk"
    ]],
    use_container_width=True
)

fig_top5_zone = px.bar(
    top5_by_zone,
    x="name",
    y="trusted_recommendation_score",
    color="berlin_zone",
    title="Top 5 Trusted ESG Hotels by Berlin Zone"
)

st.plotly_chart(fig_top5_zone, use_container_width=True)

st.divider()

#AI Data Trust Risk Distribution

st.subheader(" AI Trust Risk Distribution")

risk_counts = (
    filtered_df["final_ai_trust_risk"]
    .value_counts()
    .reset_index()
)

risk_counts.columns = ["final_ai_trust_risk", "hotel_count"]

st.dataframe(risk_counts, use_container_width=True)

fig_risk = px.pie(
    risk_counts,
    names="final_ai_trust_risk",
    values="hotel_count",
    title="Distribution of Hotels by Final AI Trust Risk"
)

st.plotly_chart(fig_risk, use_container_width=True)

st.divider()

# ESG map
st.subheader("Berlin ESG Map")

map_df = filtered_df.dropna(
    subset=["latitude", "longitude"]
)

fig_map = px.scatter_mapbox(
    map_df,
    lat="latitude",
    lon="longitude",
    color="esg_score",
    size="trusted_recommendation_score",
    hover_name="name",
    hover_data=[
        "berlin_zone",
        "hotel_class",
        "esg_class",
        "confidence_score",
        "final_ai_trust_risk"
    ],
    zoom=10,
    height=650,
    title="Hotel ESG Performance Across Berlin"
)

fig_map.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0, "t":40, "l":0, "b":0}
)

st.plotly_chart(fig_map, use_container_width=True)


st.divider()

#Carbon Hotspot Map

st.subheader(" Carbon Hotspot Map")

fig_carbon_map = px.scatter_mapbox(
    map_df,
    lat="latitude",
    lon="longitude",
    color="co2_per_occupied_room_night",
    size="co2_per_occupied_room_night",
    hover_name="name",
    hover_data=[
        "berlin_zone",
        "hotel_class",
        "esg_class",
        "co2_per_occupied_room_night",
        "confidence_score",
        "final_ai_trust_risk"
    ],
    zoom=10,
    height=650,
    title="Hotel Carbon Intensity Hotspots Across Berlin"
)

fig_carbon_map.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0, "t":40, "l":0, "b":0}
)

st.plotly_chart(fig_carbon_map, use_container_width=True)

st.divider()

#Borough ESG Analysis

st.subheader(" Borough ESG Analysis")

borough_analysis = filtered_df.groupby("borough").agg(
    hotel_count=("name", "count"),
    avg_esg_score=("esg_score", "mean"),
    avg_carbon_intensity=("co2_per_occupied_room_night", "mean"),
    avg_confidence_score=("confidence_score", "mean"),
    avg_trusted_score=("trusted_recommendation_score", "mean")
).reset_index()

borough_analysis = borough_analysis.round(2)

st.dataframe(borough_analysis, use_container_width=True)

fig_borough = px.bar(
    borough_analysis.sort_values("avg_esg_score", ascending=False),
    x="borough",
    y="avg_esg_score",
    color="avg_esg_score",
    title="Average ESG Score by Berlin Borough"
)

st.plotly_chart(fig_borough, use_container_width=True)

st.divider()

#Hotel Recommendations


st.subheader("🌱 Sustainability Recommendation Test")

hotel_search = st.text_input(
    "Enter hotel name or keyword",
    placeholder="Example: Premier Inn"
)

if st.button("Get Recommendation"):

    if hotel_search.strip() == "":
        st.warning("Please enter a hotel name or keyword.")

    else:
        matches = df[
            df["name"].astype(str).str.lower().str.contains(
                hotel_search.lower().strip(),
                na=False
            )
        ]

        if matches.empty:
            st.info("Hotel not found.")

        else:
            selected_hotel = matches.iloc[0]
            selected_zone = selected_hotel["berlin_zone"]

            better_options = df[
                (df["berlin_zone"] == selected_zone) &
                (df["name"] != selected_hotel["name"]) &
                (
                    df["trusted_recommendation_score"] >
                    selected_hotel["trusted_recommendation_score"]
                )
            ].copy()

            if better_options.empty:
                st.info(
                    f"No better trusted ESG alternative found for "
                    f"{selected_hotel['name']} in {selected_zone}."
                )

            else:
                best_alternative = better_options.sort_values(
                    by="trusted_recommendation_score",
                    ascending=False
                ).iloc[0]

                score_improvement = (
                    best_alternative["trusted_recommendation_score"] -
                    selected_hotel["trusted_recommendation_score"]
                )

                carbon_difference = (
                    selected_hotel["co2_per_occupied_room_night"] -
                    best_alternative["co2_per_occupied_room_night"]
                )

                st.success(
                    f"Instead of **{selected_hotel['name']}**, choose "
                    f"**{best_alternative['name']}** in **{selected_zone}**. "
                    f"It improves the trusted ESG score by "
                    f"**{score_improvement:.2f} points** and changes carbon "
                    f"intensity by **{carbon_difference:.2f} kg CO₂e per occupied room night**."
                )

                recommendation_df = pd.DataFrame([
                    {
                        "Selected Hotel": selected_hotel["name"],
                        "Recommended Hotel": best_alternative["name"],
                        "Berlin Zone": selected_zone,
                        "Selected Score": round(selected_hotel["trusted_recommendation_score"], 2),
                        "Recommended Score": round(best_alternative["trusted_recommendation_score"], 2),
                        "Score Improvement": round(score_improvement, 2),
                        "Selected Carbon": round(selected_hotel["co2_per_occupied_room_night"], 2),
                        "Recommended Carbon": round(best_alternative["co2_per_occupied_room_night"], 2),
                        "Carbon Difference": round(carbon_difference, 2),
                        "Selected AI Risk": selected_hotel["final_ai_trust_risk"],
                        "Recommended AI Risk": best_alternative["final_ai_trust_risk"],
                    }
                ])

                st.dataframe(
                    recommendation_df,
                    use_container_width=True
                )
