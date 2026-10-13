
import csv
import io
import time

import streamlit as st


# ==========================================
# 1. CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Smart Traffic Management",
    page_icon="🚦",
    layout="wide",
)

ROADS = ["North", "South", "East", "West"]
AMBER_TIME = 3
HIGH_TRAFFIC_LIMIT = 30
MODERATE_TRAFFIC_LIMIT = 20


# ==========================================
# 2. SESSION STATE
# ==========================================
defaults = {
    "running": False,
    "phase_index": 0,
    "phase_started": 0.0,
    "counts": {road: 10 for road in ROADS},
    "emergency_road": "None",
    "emergency_active": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# 3. DASHBOARD DESIGN
# ==========================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b1220;
        color: #f1f5f9;
    }

    [data-testid="stHeader"] {
        background-color: transparent;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMetric"] {
        background-color: #151f32;
        border: 1px solid #29364b;
        padding: 16px;
        border-radius: 12px;
    }

    div.stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
    }

    h1, h2, h3 {
        color: #f8fafc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 4. HEADER
# ==========================================
st.title("🚦 SMART TRAFFIC MANAGEMENT")
st.caption("SMART CITY • ADAPTIVE TRAFFIC MANAGEMENT")

st.write(
    "An adaptive traffic signal simulation that recommends "
    "green-light durations according to the number of vehicles "
    "waiting on each road."
)

st.info(
    "This application uses manually entered vehicle counts. "
    "It is a simulation and does not control real traffic signals."
)


# ==========================================
# 5. TRAFFIC INPUT
# ==========================================
st.header("01 | Traffic Control Center")

st.write("Enter the number of vehicles waiting on each road.")

input_cols = st.columns(4)

for i, road in enumerate(ROADS):
    with input_cols[i]:
        st.session_state.counts[road] = st.number_input(
            f"{road} Road",
            min_value=0,
            max_value=200,
            value=st.session_state.counts[road],
            step=1,
            key=f"count_{road}",
            disabled=st.session_state.running,
        )

counts = st.session_state.counts


def get_green_time(road):
    """Calculate recommended green time from the vehicle count."""
    return min(40, 10 + counts[road])


green_times = {
    road: get_green_time(road)
    for road in ROADS
}


# ==========================================
# 6. EMERGENCY VEHICLE PRIORITY
# ==========================================
st.divider()
st.header("Emergency Vehicle Priority")

emergency_options = ["None"] + ROADS

selected_emergency_road = st.selectbox(
    "Select the road where the emergency vehicle is approaching",
    emergency_options,
    key="emergency_road_selector",
    disabled=st.session_state.running,
)

emergency_col1, emergency_col2 = st.columns(2)

with emergency_col1:
    if st.button(
        "Activate Emergency Priority",
        type="primary",
        disabled=st.session_state.running,
        width="stretch",
    ):
        if selected_emergency_road != "None":
            st.session_state.emergency_road = selected_emergency_road
            st.session_state.emergency_active = True
            st.session_state.phase_started = time.time()

            st.success(
                f"Emergency priority activated for "
                f"{selected_emergency_road} Road."
            )
        else:
            st.warning(
                "Select a road before activating emergency priority."
            )

with emergency_col2:
    if st.button(
        "Cancel Emergency Priority",
        disabled=st.session_state.running,
        width="stretch",
    ):
        st.session_state.emergency_road = "None"
        st.session_state.emergency_active = False
        st.info("Emergency priority cancelled.")

if st.session_state.emergency_active:
    st.error(
        f"Emergency priority is active for "
        f"{st.session_state.emergency_road} Road."
    )


# ==========================================
# 7. SIMULATION CONTROLS
# ==========================================
button_cols = st.columns([1, 1, 3])

with button_cols[0]:
    if st.button(
        "▶ Start Simulation",
        type="primary",
        disabled=st.session_state.running,
        width="stretch",
    ):
        st.session_state.running = True

        if st.session_state.emergency_active:
            st.session_state.phase_index = ROADS.index(
                st.session_state.emergency_road
            )
        else:
            st.session_state.phase_index = 0

        st.session_state.phase_started = time.time()
        st.rerun()

with button_cols[1]:
    if st.button(
        "■ Stop Simulation",
        disabled=not st.session_state.running,
        width="stretch",
    ):
        st.session_state.running = False
        st.rerun()

st.divider()


# ==========================================
# 8. LIVE SIGNAL MONITOR
# ==========================================
@st.fragment(run_every="1s")
def live_dashboard():

    current_counts = st.session_state.counts

    current_green_times = {
        road: min(40, 10 + current_counts[road])
        for road in ROADS
    }

    st.header("02 | Live Signal Monitor")

    if not st.session_state.running:
        st.info(
            "Simulation is stopped. Press Start Simulation to begin."
        )

        cols = st.columns(4)

        for i, road in enumerate(ROADS):
            with cols[i]:
                st.markdown(f"### {road}")
                st.markdown("## 🔴 RED")
                st.caption(
                    f"{current_counts[road]} vehicles waiting"
                )

        return

    if st.session_state.emergency_active:
        road = st.session_state.emergency_road
        index = ROADS.index(road)
    else:
        index = st.session_state.phase_index
        road = ROADS[index]

    elapsed = time.time() - st.session_state.phase_started
    green_duration = current_green_times[road]
    total_duration = green_duration + AMBER_TIME

    if elapsed >= total_duration:
        st.session_state.phase_started = time.time()

        if st.session_state.emergency_active:
            st.session_state.phase_index = ROADS.index(
                st.session_state.emergency_road
            )
        else:
            st.session_state.phase_index = (
                st.session_state.phase_index + 1
            ) % len(ROADS)

        st.rerun()

    if elapsed < green_duration:
        signal_state = "GREEN"
        remaining = green_duration - elapsed
    else:
        signal_state = "AMBER"
        remaining = total_duration - elapsed

    progress = elapsed / total_duration

    metric_cols = st.columns(3)

    with metric_cols[0]:
        st.metric("ACTIVE ROAD", road)

    with metric_cols[1]:
        st.metric("SIGNAL STATUS", signal_state)

    with metric_cols[2]:
        st.metric(
            "TIME REMAINING",
            f"{max(0, int(remaining + 0.99))} sec",
        )

    st.progress(
        min(1.0, progress),
        text="Current signal phase",
    )

    signal_cols = st.columns(4)

    for i, other_road in enumerate(ROADS):
        with signal_cols[i]:
            st.markdown(f"### {other_road}")

            if other_road == road and signal_state == "GREEN":
                st.markdown("## 🟢")
                st.success("GREEN")

            elif other_road == road and signal_state == "AMBER":
                st.markdown("## 🟡")
                st.warning("AMBER")

            else:
                st.markdown("## 🔴")
                st.error("RED")

            st.caption(
                f"Vehicles: {current_counts[other_road]}"
            )

            st.caption(
                f"Recommended green time: "
                f"{current_green_times[other_road]} sec"
            )


live_dashboard()


# ==========================================
# 9. TRAFFIC ANALYTICS
# ==========================================
st.divider()
st.header("03 | Traffic Analytics")

total_vehicles = sum(counts.values())

busiest_road = max(
    ROADS,
    key=lambda road: counts[road],
)

average_vehicles = total_vehicles / len(ROADS)

metric_cols = st.columns(3)

with metric_cols[0]:
    st.metric("TOTAL VEHICLES", total_vehicles)

with metric_cols[1]:
    st.metric("BUSIEST ROAD", busiest_road)

with metric_cols[2]:
    st.metric(
        "AVERAGE PER ROAD",
        f"{average_vehicles:.1f}",
    )

st.subheader("Vehicle Count by Road")
st.bar_chart({"Vehicles": counts})

st.subheader("Road Congestion Overview")

density_data = []

for road in ROADS:
    count = counts[road]

    if count >= HIGH_TRAFFIC_LIMIT:
        density = "High"
    elif count >= 10:
        density = "Medium"
    else:
        density = "Low"

    density_data.append(
        {
            "Road": road,
            "Vehicles": count,
            "Density": density,
            "Recommended Green Time": (
                f"{green_times[road]} sec"
            ),
        }
    )

st.dataframe(
    density_data,
    width="stretch",
    hide_index=True,
)


# ==========================================
# 10. FIXED VS ADAPTIVE COMPARISON
# ==========================================
st.divider()
st.header("04 | Fixed vs Adaptive Comparison")

st.write(
    "Compare a fixed 30-second green phase with the recommended "
    "green time calculated from each road's vehicle count."
)

comparison_data = []

for road in ROADS:
    vehicles = counts[road]
    fixed_time = 30
    adaptive_time = min(40, 10 + vehicles)

    comparison_data.append(
        {
            "Road": road,
            "Vehicles": vehicles,
            "Fixed Green Time (sec)": fixed_time,
            "Adaptive Green Time (sec)": adaptive_time,
        }
    )

st.dataframe(
    comparison_data,
    width="stretch",
    hide_index=True,
)

st.subheader("Green-Time Comparison")

chart_data = {
    "Fixed (30 sec)": {
        road: 30 for road in ROADS
    },
    "Adaptive": {
        road: min(40, 10 + counts[road])
        for road in ROADS
    },
}

st.bar_chart(chart_data)

st.info(
    "Fixed timing assigns the same green duration to every road. "
    "Adaptive timing varies the recommendation according to vehicle "
    "count. This comparison alone does not establish a reduction in "
    "waiting time or congestion."
)



# ==========================================
# 07 | LANE-WISE AIR QUALITY MONITORING
# ==========================================

st.divider()
st.header("07 | Lane-Wise AQI Monitoring")

st.write(
    "Monitor air quality on each approach of the intersection "
    "and identify the lane with the highest AQI."
)

st.info(
    "Prototype mode: Enter sample AQI values below. "
    "Connect physical sensors to display actual lane readings."
)

LANES = ["North", "South", "East", "West"]

# Enter AQI readings for each lane
st.subheader("Lane Sensor Readings")

aqi_cols = st.columns(4)
lane_aqi = {}

for i, lane in enumerate(LANES):
    with aqi_cols[i]:
        lane_aqi[lane] = st.number_input(
            f"{lane} Lane AQI",
            min_value=0,
            max_value=500,
            value=50,
            step=1,
            key=f"lane_aqi_{lane}",
        )

# AQI category using the US AQI scale
def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

# Find the lane or lanes with the highest AQI
highest_aqi = max(lane_aqi.values())

highest_lanes = [
    lane for lane, value in lane_aqi.items()
    if value == highest_aqi
]

# Highest-AQI alert
st.subheader("Highest AQI Detection")

if len(highest_lanes) == 1:
    st.error(
        f"⚠️ Highest AQI Lane: {highest_lanes[0]} "
        f"| AQI: {highest_aqi}"
    )
else:
    st.warning(
        f"⚠️ Highest AQI is shared by "
        f"{', '.join(highest_lanes)} "
        f"| AQI: {highest_aqi}"
    )

st.caption(
    f"AQI Category: {get_aqi_category(highest_aqi)}"
)

# Display lane-wise AQI cards
st.subheader("Lane-Wise Air Quality Dashboard")

display_cols = st.columns(4)

for i, lane in enumerate(LANES):
    value = lane_aqi[lane]
    category = get_aqi_category(value)

    with display_cols[i]:
        st.metric(
            label=f"{lane} Lane",
            value=value,
        )

        st.caption(category)

        if value == highest_aqi:
            st.error("Highest AQI")
        elif value <= 50:
            st.success("Good Air Quality")
        elif value <= 100:
            st.info("Moderate Air Quality")
        else:
            st.warning("Elevated AQI")

# Comparison chart
st.subheader("AQI Comparison Across Four Lanes")

st.bar_chart(
    {"AQI": lane_aqi},
    x_label="Lane",
    y_label="US AQI",
)

# Lane-wise report
st.subheader("Lane-Wise AQI Report")

aqi_report = []

for lane in LANES:
    value = lane_aqi[lane]

    aqi_report.append({
        "Lane": lane,
        "AQI": value,
        "Category": get_aqi_category(value),
        "Highest AQI": "Yes" if value == highest_aqi else "No",
    })

st.dataframe(
    aqi_report,
    width="stretch",
    hide_index=True,
)

st.caption(
    "AQI comparison currently uses manually entered values. "
    "The categories follow the US AQI scale. Physical sensors "
    "and a validated measurement method are required for real readings."
)


# ==========================================
# 11. TRAFFIC ALERTS
# ==========================================
st.divider()
st.header("05 | Traffic Alerts")

st.write(
    "Vehicle counts are checked against configured thresholds "
    "to identify roads that may need attention."
)

high_roads = [
    (road, counts[road])
    for road in ROADS
    if counts[road] >= HIGH_TRAFFIC_LIMIT
]

moderate_roads = [
    (road, counts[road])
    for road in ROADS
    if MODERATE_TRAFFIC_LIMIT
    <= counts[road] < HIGH_TRAFFIC_LIMIT
]

if high_roads:
    st.error(
        f"HIGH CONGESTION: {len(high_roads)} road(s) "
        "have reached the high-traffic threshold."
    )

elif moderate_roads:
    st.warning(
        "MODERATE TRAFFIC: One or more roads have increased "
        "vehicle counts."
    )

else:
    st.success(
        "TRAFFIC NORMAL: No road has reached the "
        "moderate-traffic threshold."
    )

st.subheader("Road-wise Alert Status")

for road in ROADS:
    vehicles = counts[road]

    if vehicles >= HIGH_TRAFFIC_LIMIT:
        st.error(
            f"{road}: {vehicles} vehicles — High traffic level. "
            "Review the recommended green time."
        )

    elif vehicles >= MODERATE_TRAFFIC_LIMIT:
        st.warning(
            f"{road}: {vehicles} vehicles — Moderate traffic level."
        )

    else:
        st.success(
            f"{road}: {vehicles} vehicles — Normal traffic level."
        )

st.caption(
    "Alert levels use manually entered counts and configured "
    "thresholds; they are not measurements of real-world congestion."
)


# ==========================================
# 12. DOWNLOADABLE TRAFFIC REPORT
# ==========================================
st.divider()
st.header("06 | Download Traffic Report")

st.write(
    "Export the current vehicle counts, green-time recommendations, "
    "and traffic classifications as a CSV file."
)

report = io.StringIO()
writer = csv.writer(report)

writer.writerow(
    [
        "Road",
        "Vehicle Count",
        "Fixed Green Time (sec)",
        "Adaptive Green Time (sec)",
        "Traffic Status",
    ]
)

for road in ROADS:
    vehicles = counts[road]

    if vehicles >= HIGH_TRAFFIC_LIMIT:
        status = "High Traffic"

    elif vehicles >= MODERATE_TRAFFIC_LIMIT:
        status = "Moderate Traffic"

    else:
        status = "Normal"

    writer.writerow(
        [
            road,
            vehicles,
            30,
            min(40, 10 + vehicles),
            status,
        ]
    )

st.download_button(
    label="📥 Download Traffic Report (CSV)",
    data=report.getvalue(),
    file_name="smart_traffic_report.csv",
    mime="text/csv",
    width="stretch",
)

st.caption(
    "The report reflects the vehicle counts currently entered "
    "in the application."
)


# ==========================================
# 13. FOOTER
# ==========================================
st.divider()

st.caption("Smart Traffic Management | Python + Streamlit")

st.caption(
    "Simulation only. Real traffic control requires validated signal "
    "phases, conflict checks, and safety interlocks."
)
