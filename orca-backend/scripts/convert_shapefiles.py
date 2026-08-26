"""
Shapefile → GeoJSON Converter for ORCA Maritime Datasets

Converts Natural Earth land polygons and Marine Regions EEZ shapefiles
to GeoJSON format, optionally clipping to a bounding box.

Usage:
    python scripts/convert_shapefiles.py --input ne_10m_land.shp --output app/data/land_polygons.geojson --bbox 65,5,90,25

Requirements:
    pip install shapely fiona

If fiona is not available, use QGIS or ogr2ogr instead:
    ogr2ogr -f GeoJSON -clipdst 65 5 90 25 land_polygons.geojson ne_10m_land.shp
"""
import argparse
import json
import sys


def convert_with_pyshp(input_path: str, output_path: str, bbox: list = None):
    """Convert shapefile to GeoJSON using pure-python shapefile (pyshp) + shapely."""
    try:
        import shapefile
        from shapely.geometry import shape, mapping, box
    except ImportError:
        print("ERROR: 'pyshp' and/or 'shapely' not installed.")
        print("Install with: pip install pyshp shapely")
        print("pyshp is pure Python and installs easily on Windows without GDAL/C-library errors.")
        sys.exit(1)

    clip_box = None
    if bbox:
        clip_box = box(bbox[0], bbox[1], bbox[2], bbox[3])  # minx, miny, maxx, maxy

    features = []
    print(f"Reading shapefile: {input_path}")
    
    with shapefile.Reader(input_path) as reader:
        # Get shapefile records
        shapes = reader.shapes()
        records = reader.records()
        fields = [f[0] for f in reader.fields[1:]] # Skip DeletionFlag
        
        print(f"Loaded {len(shapes)} shapes from shapefile")
        
        for i, shp in enumerate(shapes):
            if shp.shapeType == 0: # Null shape
                continue
                
            # Convert to shapely geometry via geo interface
            geom = shape(shp.__geo_interface__)
            
            if clip_box:
                if not geom.intersects(clip_box):
                    continue
                geom = geom.intersection(clip_box)
                if geom.is_empty:
                    continue

            # Build properties dict
            props = {}
            if i < len(records):
                props = {fields[j]: records[i][j] for j in range(len(fields))}

            features.append({
                "type": "Feature",
                "properties": props,
                "geometry": mapping(geom)
            })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_path, 'w') as f:
        json.dump(geojson, f)

    print(f"Successfully wrote {len(features)} features to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert Shapefile to GeoJSON for ORCA")
    parser.add_argument("--input", required=True, help="Input shapefile path (.shp)")
    parser.add_argument("--output", required=True, help="Output GeoJSON path (.geojson)")
    parser.add_argument("--bbox", default=None,
                        help="Bounding box to clip: minlon,minlat,maxlon,maxlat (e.g. 65,5,90,25)")

    args = parser.parse_args()

    bbox = None
    if args.bbox:
        bbox = [float(x) for x in args.bbox.split(",")]
        if len(bbox) != 4:
            print("ERROR: bbox must have exactly 4 values: minlon,minlat,maxlon,maxlat")
            sys.exit(1)

    convert_with_pyshp(args.input, args.output, bbox)


if __name__ == "__main__":
    main()
