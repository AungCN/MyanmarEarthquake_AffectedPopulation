# Myanmar Earthquake Affected Population Analysis & Geospatial Dashboard

Geospatial impact assessment, population exposure estimation, and interactive **Streamlit + Folium** mapping dashboards analyzing earthquake events across Myanmar and estimating affected township populations using census and MIMU household datasets.

## Repository Structure

- **Root Scripts & Notebooks**
  - `myanmar_earthquake_affected_final_V14Apr.ipynb` / `myanmar_earthquake_affected3.ipynb` — Comprehensive notebooks estimating affected population within distance radii of earthquake epicenters using geodesic distance calculations and machine learning regression (Random Forest, XGBoost, LSTM).
  - `mmearthquake_final1.py` & `myanmar_earthquake_affected3.py` — Python scripts for earthquake impact estimation and interactive geospatial visualization.
- **`mm_earthquake_final_20250401/`**
  - Streamlit geospatial dashboard apps (`myanmar_earthquake_affected_final_1.py`, `earthquake_test_csv2.py`, `neweqmap.py`) and curated township population (`MyanmarPop_2014_Township.csv`) & USGS earthquake datasets (`earthquake_data_myanmar.csv`, `earthquake_data_global.csv`).
- **`testingpython/` & `mmEarthquake_Old/`**
  - Historical data snapshots, MIMU township household datasets, 2019 Inter-censal population tables, and prototype scripts.

## Setup & Usage

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/AungCN/MyanmarEarthquake_AffectedPopulation.git
   cd MyanmarEarthquake_AffectedPopulation
   pip install -r requirements.txt
   ```
2. Run the Streamlit dashboard:
   ```bash
   cd mm_earthquake_final_20250401
   streamlit run myanmar_earthquake_affected_final_1.py
   ```

## License

This project is licensed under the [MIT License](LICENSE).
