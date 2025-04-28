# PaperMap

**PaperMap** is a Streamlit-based web application designed to help researchers quickly generate publication-quality study area maps for scientific manuscripts. The app provides a step-by-step interface to upload site data, customize study area maps, generate multi-scale overview maps (India, State, District), and export a composite figure suitable for research papers.

## Features

- **Intuitive Interface:** User-friendly stepwise navigation for data upload, map customization, and final layout download.
- **Flexible Data Input:** Accepts `.csv`, `.xls`, or `.xlsx` files containing site name, latitude, and longitude.
- **Robust Latitude/Longitude Parsing:** Handles decimal degrees, DMS, and various common coordinate notations.
- **Auto-Detection:** Automatically detects latitude, longitude, and site columns for ease of use.
- **Map Customization:**  
  - **Basemap selection** (OpenStreetMap, CartoDB, Esri)
  - **Custom marker styles:** color, shape, size
  - **Label styling:** font size, color, weight, offsets
  - **North arrow & scale bar** (with flexible placement and units)
- **Automatic Administrative Detection:** Identifies State and District for each point, allowing instant overview mapping.
- **Composite Layout Generation:** Exports a single, ready-to-publish PNG containing the India, State, District, and study area maps in a research-friendly format.

## App Structure

1. **Welcome Page:** Introduction, app logo, and navigation.
2. **Data Upload & Study Area Map:** Data file upload, column selection, map customization, and download.
3. **Overview Maps:** Auto-generation of India, State, and District overview maps based on detected locations.
4. **Composite Layout & Download:** Combine all maps into a single composite figure for download.

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/papermap.git
   cd papermap
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or install individually:
   ```bash
   pip install streamlit pandas geopandas matplotlib shapely contextily pillow
   ```

3. **Prepare assets and data:**
   - Place `PaperMap_logo.png` and `north_arrow.png` in the `assets/` directory.
   - Place shapefiles `India_State_Boundary_UPPERCASE.shp` and `DISTRICT_BOUNDARY_CLEANED.shp` in the `data/` directory.

## Usage

Run the app with:

```bash
streamlit run 00_🏠_Welcome.py
```

Or start at any page (for development):

```bash
streamlit run 01_🟢_Data_Upload_and_Study_Area_Map.py
```

## File/Folder Structure

```
.
├── 00_🏠_Welcome.py
├── 01_🟢_Data_Upload_and_Study_Area_Map.py
├── 02_🗺️_Overview_Maps.py
├── 03_🖼️_Composite_Layout_and_Download.py
├── utils/
│   └── geo_utils.py
├── assets/
│   ├── PaperMap_logo.png
│   └── north_arrow.png
├── data/
│   ├── India_State_Boundary_UPPERCASE.shp
│   └── DISTRICT_BOUNDARY_CLEANED.shp
└── requirements.txt
```

## Data Format

Upload a `.csv`, `.xls`, or `.xlsx` file with at least these columns:
- **Site name** (e.g., Site, Station, Location, etc.)
- **Latitude** (in any standard format: decimal, DMS, etc.)
- **Longitude** (in any standard format)

## License

[MIT License](LICENSE) – Free for academic and research use.

## Acknowledgments

- [Streamlit](https://streamlit.io/)
- [GeoPandas](https://geopandas.org/)
- [Matplotlib](https://matplotlib.org/)
- [Contextily](https://contextily.readthedocs.io/)

---
