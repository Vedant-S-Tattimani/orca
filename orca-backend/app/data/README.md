# ORCA Maritime Navigation — Dataset Instructions

## Required Data Files

Place the following files in this directory (`app/data/`).

### 1. GEBCO Bathymetry (Regional Subset)

**File:** `gebco_indian_ocean.nc`
**Format:** NetCDF
**Source:** [GEBCO Gridded Bathymetry Data](https://www.gebco.net/data-products/gridded-bathymetry-data/)

**Download steps:**
1. Go to https://download.gebco.net/
2. Select the "GEBCO Sub-Cell" or "Grid" product
3. Set the bounding box:
   - North: 25.0
   - South: 5.0
   - West: 65.0
   - East: 90.0
4. Select format: **NetCDF**
5. Download and place the `.nc` file here as `gebco_indian_ocean.nc`

**File size:** ~25–30 MB

---

### 2. Natural Earth Land Polygons

**File:** `land_polygons.geojson`
**Format:** GeoJSON
**Source:** [Natural Earth 1:10m Land](https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/)

**Download steps:**
1. Download `ne_10m_land.zip` from Natural Earth
2. Extract the Shapefile
3. Convert to GeoJSON using QGIS, `ogr2ogr`, or the included `scripts/convert_shapefiles.py`:
   ```
   python scripts/convert_shapefiles.py --input ne_10m_land.shp --output app/data/land_polygons.geojson --bbox 65,5,90,25
   ```
4. Place the result here as `land_polygons.geojson`

**Alternatively:** If you have `ogr2ogr` installed:
```bash
ogr2ogr -f GeoJSON -clipdst 65 5 90 25 land_polygons.geojson ne_10m_land.shp
```

---

### 3. Marine Regions EEZ (Optional)

**File:** `india_eez.geojson`
**Format:** GeoJSON
**Source:** [Marine Regions Downloads](https://www.marineregions.org/downloads.php)

This file is optional. If present, it provides EEZ boundary awareness.

**Download steps:**
1. Download the World EEZ v12 Shapefile from Marine Regions
2. Extract and filter to India's EEZ
3. Convert to GeoJSON and place here as `india_eez.geojson`

---

## Notes

- All datasets are free for academic/research/educational use (including SIH demonstrations)
- GEBCO data is NOT navigation-grade. Do not use for actual vessel navigation
- If any file is missing, the routing engine will fall back to the existing `COASTAL_FALLBACK` mode
- The graph will be built from these files on first startup and cached as `maritime_graph.pkl`
