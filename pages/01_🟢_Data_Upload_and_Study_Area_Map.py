import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, box
import numpy as np
import contextily as ctx
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import io
from utils.geo_utils import add_map_border, add_scalebar  # Assuming these exist in your project

import re

# --- Robust latitude/longitude parser ---
def parse_latlon(val):
    """
    Converts a wide range of latitude/longitude string formats to decimal degrees float.
    Supports:
      - Decimal degrees: 9.9732, -9.9732, 9.9732N, 76.2821E, etc.
      - DMS: 9°58'23"N, 76°16'56"E, 9 58 23 N, 9:58:23S, etc.
      - Degrees and decimal minutes: 9°58.383'N, 76 16.934 W, etc.
      - Any whitespace, delimiter or symbol
    Returns NaN if format is unrecognized.
    """
    if isinstance(val, (float, int)) and not isinstance(val, bool):
        return float(val)
    if not isinstance(val, str):
        return np.nan

    s = val.strip().replace(" ", "").replace("º", "°").replace("’", "'").replace("”", '"').replace("′", "'").replace("″", '"')

    # Decimal degrees with direction (e.g., 9.9732N, 76.2821W)
    m = re.match(r"^([-+]?\d+(?:\.\d+)?)([NSEW])?$", s, re.IGNORECASE)
    if m:
        num = float(m.group(1))
        direction = m.group(2)
        if direction:
            if direction.upper() in ['S', 'W']:
                num = -abs(num)
            else:
                num = abs(num)
        return num

    # DMS or DM with possible direction: e.g., 9°58'23"N, 9:58:23N, 76°16.934'W
    dms_pattern = (
        r"^([-\d\.]+)[°:]([-\d\.]+)?[':]?([-\d\.]+)?\"?([NSEW])?$"
    )
    m = re.match(dms_pattern, s, re.IGNORECASE)
    if m:
        deg = float(m.group(1))
        min_ = float(m.group(2)) if m.group(2) else 0
        sec = float(m.group(3)) if m.group(3) else 0
        direction = m.group(4)
        num = abs(deg) + min_ / 60 + sec / 3600
        if deg < 0:  # preserve negative degrees
            num = -num
        if direction:
            if direction.upper() in ['S', 'W']:
                num = -abs(num)
            else:
                num = abs(num)
        return num

    # Space or colon separated: "9 58 23N" or "9:58:23N"
    m = re.match(r"^([-\d\.]+)[ :]+([-\d\.]+)(?:[ :]+([-\d\.]+))?([NSEW])?$", val.replace("º", "°"), re.IGNORECASE)
    if m:
        deg = float(m.group(1))
        min_ = float(m.group(2))
        sec = float(m.group(3)) if m.group(3) else 0
        direction = m.group(4)
        num = abs(deg) + min_ / 60 + sec / 3600
        if deg < 0:
            num = -num
        if direction:
            if direction.upper() in ['S', 'W']:
                num = -abs(num)
            else:
                num = abs(num)
        return num

    # Single degree with direction: "9N", "76E"
    m = re.match(r"^(\d+)([NSEW])$", s, re.IGNORECASE)
    if m:
        num = float(m.group(1))
        direction = m.group(2)
        if direction.upper() in ['S', 'W']:
            num = -abs(num)
        else:
            num = abs(num)
        return num

    # Fallback: try to parse as float
    try:
        return float(val)
    except Exception:
        return np.nan

# --- Column auto-detection logic ---
def auto_detect_column(cols, keywords):
    for key in keywords:
        for col in cols:
            norm_col = col.strip().lower().replace(" ", "").replace("_", "")
            if key == norm_col:
                return col
    return None

def auto_detect_site_column(columns, lat_col, lon_col, site_keys):
    # 1. Try keyword-based match
    for key in site_keys:
        for col in columns:
            norm_col = col.strip().lower().replace(" ", "").replace("_", "")
            if key == norm_col:
                return col
    # 2. Fallback: left of lat/lon
    try:
        lat_idx = columns.index(lat_col)
        if lat_idx > 0:
            return columns[lat_idx - 1]
    except ValueError:
        pass
    try:
        lon_idx = columns.index(lon_col)
        if lon_idx > 0:
            return columns[lon_idx - 1]
    except ValueError:
        pass
    # 3. Fallback: right of lat/lon
    try:
        lat_idx = columns.index(lat_col)
        if lat_idx < len(columns) - 1:
            return columns[lat_idx + 1]
    except ValueError:
        pass
    try:
        lon_idx = columns.index(lon_col)
        if lon_idx < len(columns) - 1:
            return columns[lon_idx + 1]
    except ValueError:
        pass
    return None

# ---- Streamlit App ----
st.set_page_config(page_title="Data Upload & Study Area Map", layout="wide")
st.title("🟢 Data Upload & Study Area Map")

with st.sidebar:
    uploaded_file = st.file_uploader(
        "Upload CSV, XLS, or XLSX with Latitude & Longitude",
        type=["csv", "xls", "xlsx"]
    )

    state_shapefile_path = "data/India_State_Boundary_UPPERCASE.shp"
    district_shapefile_path = "data/DISTRICT_BOUNDARY_CLEANED.shp"

    site_col = lat_col = lon_col = None

    if uploaded_file:
        file_type = uploaded_file.name.split('.')[-1].lower()
        if file_type in ['xls', 'xlsx']:
            df = pd.read_excel(uploaded_file)
        elif file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a CSV, XLS, or XLSX file.")
            st.stop()
        df.columns = df.columns.str.strip()
        columns = df.columns.tolist()

        # --- Auto-detect lat/lon columns ---
        lat_keys = ['lat', 'latitude', 'y']
        lon_keys = ['lon', 'lng', 'long', 'longitude', 'x']
        site_keys = ['site', 'sitename', 'station', 'location', 'place', 'sampleid', 'name', 'point']

        auto_lat = auto_detect_column(columns, lat_keys)
        auto_lon = auto_detect_column(columns, lon_keys)

        # Only try to auto-detect site_col once lat/lon found
        if auto_lat or auto_lon:
            auto_site = auto_detect_site_column(columns, auto_lat or "", auto_lon or "", site_keys)
        else:
            auto_site = auto_detect_column(columns, site_keys)

        site_col = st.selectbox(
            "Site Name column", ["Select"] + columns,
            index=(columns.index(auto_site) + 1) if auto_site in columns else 0,
            key="site_col"
        )
        lat_col = st.selectbox(
            "Latitude column", ["Select"] + columns,
            index=(columns.index(auto_lat) + 1) if auto_lat in columns else 0,
            key="lat_col"
        )
        lon_col = st.selectbox(
            "Longitude column", ["Select"] + columns,
            index=(columns.index(auto_lon) + 1) if auto_lon in columns else 0,
            key="lon_col"
        )

        if all(x != "Select" for x in [site_col, lat_col, lon_col]):
            # --- Apply robust lat/lon parser here! ---
            df[lat_col] = df[lat_col].apply(parse_latlon)
            df[lon_col] = df[lon_col].apply(parse_latlon)
            if df[lat_col].isnull().any() or df[lon_col].isnull().any():
                st.error("Some latitude/longitude values could not be parsed. Please check your input format.")
                st.stop()

            # --- Basemap selection ---
            with st.expander("🗺️ Basemap Style", expanded=False):
                basemap_options = {
                    "OpenStreetMap": ctx.providers.OpenStreetMap.Mapnik,
                    "CartoDB Positron": ctx.providers.CartoDB.Positron,
                    "Esri World Topo": ctx.providers.Esri.WorldTopoMap,
                    "Esri Standard Streets": ctx.providers.Esri.WorldStreetMap
                }
                selected_basemap = st.selectbox("Choose a basemap", list(basemap_options.keys()))

            # --- Scale bar settings ---
            with st.expander("📏 Scale Bar Settings", expanded=False):
                scalebar_unit = st.selectbox("Scale Bar Unit", ["meters", "kilometers"], index=1)
                scalebar_length = st.slider(
                    "Scale Bar Length (meters)" if scalebar_unit == "meters" else "Scale Bar Length (km)",
                    100 if scalebar_unit == "meters" else 0.5,
                    10000 if scalebar_unit == "meters" else 5.0,
                    2000 if scalebar_unit == "meters" else 2.0,
                    100 if scalebar_unit == "meters" else 0.5,
                )
                st.session_state.setdefault('scalebar_offset_x', 0.75)
                st.session_state.setdefault('scalebar_offset_y', 0.05)
                st.number_input("Scalebar X Offset", 0.0, 1.0, st.session_state.scalebar_offset_x, 0.01, key="scalebar_offset_x_input")
                st.number_input("Scalebar Y Offset", 0.0, 1.0, st.session_state.scalebar_offset_y, 0.01, key="scalebar_offset_y_input")
                st.session_state.scalebar_offset_x = st.session_state.scalebar_offset_x_input
                st.session_state.scalebar_offset_y = st.session_state.scalebar_offset_y_input

            # --- Label Styling ---
            with st.expander("🏷️ Label Styling", expanded=False):
                label_fontsize = st.slider("Label Font Size", 6, 24, 9)
                label_color = st.color_picker("Label Color", "#000000")
                label_weight = st.selectbox("Label Font Weight", ["normal", "bold"])
                label_offset_x = st.slider("Label X Offset (px)", -30, 30, 0)
                label_offset_y = st.slider("Label Y Offset (px)", -30, 30, 0)
                label_bg_enabled = st.checkbox("Enable Label Background", value=False)
                label_bg_color = "#ffffff"
                if label_bg_enabled:
                    label_bg_color = st.color_picker("Label Background Color", "#ffffff")

            # --- Marker Styling ---
            with st.expander("📍 Marker Styling", expanded=False):
                marker_color = st.color_picker("Marker Color", "#ff0000")
                marker_size = st.slider("Marker Size", 10, 300, 50)
                shape_options = {
                    "○": "o",
                    "◻": "s",
                    "△": "^",
                    "▽": "v",
                    "◇": "D",
                    "✩": "*",
                    "+": "+"
                }
                selected_shape_label = st.selectbox("Marker Shape", list(shape_options.keys()))
                marker_shape = shape_options[selected_shape_label]

            # --- North Arrow Position & Size ---
            with st.expander("🧭 North Arrow Position & Size", expanded=False):
                st.session_state.setdefault('arrow_offset_x', 0.92)
                st.session_state.setdefault('arrow_offset_y', 0.92)
                st.session_state.setdefault('arrow_zoom', 0.06)
                st.number_input("Arrow X Offset", 0.0, 1.0, st.session_state.arrow_offset_x, 0.01, key="arrow_offset_x_input")
                st.number_input("Arrow Y Offset", 0.0, 1.0, st.session_state.arrow_offset_y, 0.01, key="arrow_offset_y_input")
                st.session_state.arrow_offset_x = st.session_state.arrow_offset_x_input
                st.session_state.arrow_offset_y = st.session_state.arrow_offset_y_input
                st.session_state.arrow_zoom = st.slider("Zoom", 0.01, 0.15, st.session_state.arrow_zoom, 0.01)

# --- Main Area: Map Plotting ---
if uploaded_file and all(x != "Select" for x in [site_col, lat_col, lon_col]):
    map_placeholder = st.empty()
    with st.spinner("Generating your map..."):
        # 1. Prepare GeoDataFrames
        df = df.copy()
        gdf = gpd.GeoDataFrame(
            df, geometry=[Point(xy) for xy in zip(df[lon_col], df[lat_col])], crs="EPSG:4326"
        )
        gdf_web = gdf.to_crs(epsg=3857)
        states_gdf = gpd.read_file(state_shapefile_path).to_crs("EPSG:4326")
        districts_gdf = gpd.read_file(district_shapefile_path).to_crs("EPSG:4326")

        # Remove join index columns before spatial join
        for col in ['index_left', 'index_right']:
            if col in gdf.columns:
                gdf = gdf.drop(columns=[col])
            if col in states_gdf.columns:
                states_gdf = states_gdf.drop(columns=[col])
            if col in districts_gdf.columns:
                districts_gdf = districts_gdf.drop(columns=[col])

        # 2. State/District Detection
        points_with_state = gpd.sjoin(gdf, states_gdf[['State_Name', 'geometry']], how='left', predicate='within')
        for col in ['index_left', 'index_right']:
            if col in points_with_state.columns:
                points_with_state = points_with_state.drop(columns=[col])
            if col in districts_gdf.columns:
                districts_gdf = districts_gdf.drop(columns=[col])

        points_with_district = gpd.sjoin(points_with_state, districts_gdf[['STATE', 'District', 'geometry']], how='left', predicate='within')

        most_common_state = points_with_district['State_Name'].mode().iloc[0] if not points_with_district['State_Name'].isnull().all() else ""
        unique_districts = points_with_district['District'].dropna().unique().tolist()
        st.session_state.detected_state = most_common_state
        st.session_state.covered_districts = unique_districts
        district_bounds = districts_gdf[districts_gdf['District'].isin(unique_districts)].total_bounds
        st.session_state.district_bounds_extent = district_bounds.tolist()
        st.info(f"Detected State: **{most_common_state}**\nDetected District(s): **{', '.join(unique_districts) if unique_districts else 'None'}**")

        # 3. Plot Map
        fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
        gdf_web.plot(ax=ax, color=marker_color, edgecolor='black',
                     markersize=marker_size, marker=marker_shape)
        minx, miny, maxx, maxy = gdf_web.total_bounds
        pad_x = (maxx - minx) * 0.15
        pad_y = (maxy - miny) * 0.15
        minx_padded, maxx_padded = minx - pad_x, maxx + pad_x
        miny_padded, maxy_padded = miny - pad_y, maxy + pad_y
        st.session_state['study_area_extent'] = [minx_padded, miny_padded, maxx_padded, maxy_padded]
        ax.set_xlim(minx_padded, maxx_padded)
        ax.set_ylim(miny_padded, maxy_padded)

        # --- Add lat/lon degree axes ticks and labels ---
        bbox_geo = gpd.GeoSeries([box(minx_padded, miny_padded, maxx_padded, maxy_padded)], crs="EPSG:3857").to_crs("EPSG:4326")
        lon_min, lat_min, lon_max, lat_max = bbox_geo.total_bounds
        num_ticks = 5
        lat_ticks = np.linspace(lat_min, lat_max, num_ticks)
        lon_ticks = np.linspace(lon_min, lon_max, num_ticks)
        xtick_points = gpd.GeoSeries([Point(lon, lat_min) for lon in lon_ticks], crs="EPSG:4326").to_crs("EPSG:3857")
        ytick_points = gpd.GeoSeries([Point(lon_min, lat) for lat in lat_ticks], crs="EPSG:4326").to_crs("EPSG:3857")
        ax.set_xticks(xtick_points.geometry.x)
        ax.set_xticklabels([f"{lon:.2f}°E" for lon in lon_ticks], fontsize=10)
        ax.set_yticks(ytick_points.geometry.y)
        ax.set_yticklabels([f"{lat:.2f}°N" for lat in lat_ticks], fontsize=10)
        ax.tick_params(labelsize=10, direction='out', top=True, right=True)
        ax.set_xlabel("Longitude", fontsize=12)
        ax.set_ylabel("Latitude", fontsize=12)
        ax.grid(True, linestyle='--', linewidth=0.5)

        for idx, row in gdf_web.iterrows():
            text_kwargs = dict(
                fontsize=label_fontsize, color=label_color,
                fontweight=label_weight, ha='left', va='bottom'
            )
            if label_bg_enabled:
                text_kwargs["bbox"] = dict(facecolor=label_bg_color, edgecolor='none', boxstyle='round,pad=0.2')
            ax.text(
                row.geometry.x + (label_offset_x * pad_x / 100),
                row.geometry.y + (label_offset_y * pad_y / 100),
                str(row[site_col]), **text_kwargs
            )
        try:
            ctx.add_basemap(ax, source=basemap_options[selected_basemap], crs=gdf_web.crs.to_string())
        except Exception as e:
            st.warning(f"⚠️ Failed to load basemap: {e}")

        add_scalebar(ax, scalebar_length, scalebar_unit, offset_x=st.session_state.scalebar_offset_x, offset_y=st.session_state.scalebar_offset_y)
        try:
            north_arrow_path = "assets/north_arrow.png"
            arrow_img = mpimg.imread(north_arrow_path)
            imagebox = OffsetImage(arrow_img, zoom=st.session_state.arrow_zoom)
            ab = AnnotationBbox(imagebox, (st.session_state.arrow_offset_x, st.session_state.arrow_offset_y), xycoords='axes fraction', frameon=False)
            ax.add_artist(ab)
        except Exception as e:
            st.warning(f"⚠️ North arrow image could not be loaded: {e}")

        add_map_border(ax)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
        buf.seek(0)

    with map_placeholder.container():
        st.pyplot(fig, use_container_width=True)
        st.download_button("📥 Download Map as PNG", data=buf, file_name="study_area_map.png", mime="image/png", use_container_width=True)
        st.session_state['study_area_map'] = buf

    # --- Navigation ---
    if st.button("Next: Overview Maps ➡️"):
        st.switch_page("pages/02_🗺️_Overview_Maps.py")
