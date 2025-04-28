import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import io
from utils.geo_utils import add_map_border, add_latlon_ticks, square_bounds_with_buffer

st.set_page_config(page_title="Overview Maps", layout="wide")
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("assets/PaperMap_logo.png", width=180)
st.title("🗺️ Overview Maps")

state_shapefile_path = "data/India_State_Boundary_UPPERCASE.shp"
district_shapefile_path = "data/DISTRICT_BOUNDARY_CLEANED.shp"

detected_state = st.session_state.get('detected_state', "")
covered_districts = st.session_state.get("covered_districts", [])

if detected_state:
    states_gdf = gpd.read_file(state_shapefile_path).to_crs("EPSG:4326")
    districts_gdf = gpd.read_file(district_shapefile_path).to_crs("EPSG:4326")
    matching_districts = districts_gdf[
        (districts_gdf['STATE'] == detected_state) & (districts_gdf['District'].isin(covered_districts))
    ]
    # --- India Map ---
    fig1, ax1 = plt.subplots(figsize=(6, 6), dpi=100)
    states_gdf.plot(ax=ax1, color="#e5e5e5", edgecolor="black", linewidth=0.5, zorder=1)
    states_gdf[states_gdf['State_Name'] == detected_state].plot(ax=ax1, color="#ff6666", edgecolor="black", linewidth=2.5, zorder=2)
    bounds1 = square_bounds_with_buffer(states_gdf.total_bounds, 0.05)
    ax1.set_xlim(bounds1[0], bounds1[1])
    ax1.set_ylim(bounds1[2], bounds1[3])
    add_latlon_ticks(ax1, bounds1)
    add_map_border(ax1)
    buf1 = io.BytesIO()
    fig1.savefig(buf1, format="png", dpi=100, bbox_inches='tight', pad_inches=0.06)
    plt.close(fig1)
    buf1.seek(0)
    st.image(buf1, caption="India Overview Map")
    st.session_state['india_map'] = buf1

    # --- State Map ---
    fig2, ax2 = plt.subplots(figsize=(6, 6), dpi=100)
    state_geom = states_gdf[states_gdf['State_Name'] == detected_state]
    state_districts = districts_gdf[districts_gdf['STATE'] == detected_state]
    state_districts.plot(ax=ax2, color="#e5e5e5", edgecolor="black", linewidth=0.7, zorder=1)
    matching_districts.plot(ax=ax2, color="#ff6666", edgecolor="black", linewidth=2.0, zorder=2)
    state_geom.boundary.plot(ax=ax2, color="black", linewidth=2, zorder=3)
    if not state_geom.empty:
        bounds2 = square_bounds_with_buffer(state_geom.total_bounds, 0.05)
        ax2.set_xlim(bounds2[0], bounds2[1])
        ax2.set_ylim(bounds2[2], bounds2[3])
        add_latlon_ticks(ax2, bounds2)
        add_map_border(ax2)
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format="png", dpi=100, bbox_inches='tight', pad_inches=0.06)
    plt.close(fig2)
    buf2.seek(0)
    st.image(buf2, caption="State Overview Map")
    st.session_state['state_map'] = buf2

    # --- District Map ---
    fig3, ax3 = plt.subplots(figsize=(6, 6), dpi=100)
    if not matching_districts.empty:
        matching_districts.plot(ax=ax3, color="none", edgecolor="black", linewidth=2.5, zorder=2)
        bounds3 = square_bounds_with_buffer(matching_districts.total_bounds, 0.05)
        ax3.set_xlim(bounds3[0], bounds3[1])
        ax3.set_ylim(bounds3[2], bounds3[3])
        add_latlon_ticks(ax3, bounds3)
        add_map_border(ax3)
        # Draw study area rectangle if available (updated)
        study_area_extent = st.session_state.get('study_area_extent', None)
        if study_area_extent is not None:
            from shapely.geometry import box as shapely_box
            import geopandas as gpd
            study_area_box = shapely_box(*study_area_extent)
            study_area_gdf = gpd.GeoDataFrame(geometry=[study_area_box], crs="EPSG:3857").to_crs("EPSG:4326")
            minx, miny, maxx, maxy = study_area_gdf.total_bounds
            rect = plt.Rectangle(
                (minx, miny), maxx - minx, maxy - miny,
                linewidth=2, edgecolor='red', facecolor='none', linestyle='--', zorder=3
            )
            ax3.add_patch(rect)
    buf3 = io.BytesIO()
    fig3.savefig(buf3, format="png", dpi=100, bbox_inches='tight', pad_inches=0.06)
    plt.close(fig3)
    buf3.seek(0)
    st.image(buf3, caption="District Overview Map")
    st.session_state['district_map'] = buf3




    # --- Navigation ---
    if st.button("Next: Composite Layout ➡️"):
        st.switch_page("pages/03_🖼️_Composite_Layout_and_Download.py")
else:
    st.warning("No detected state. Please finish the previous step.")
