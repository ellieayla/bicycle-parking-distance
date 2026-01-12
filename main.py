from typing import List, Tuple
import json
from pathlib import Path


from geojson import Feature, Point, FeatureCollection, LineString
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree


EARTH_RADIUS_KM = 6371.009


def df_from_osm_json_file(json_file: Path) -> pd.DataFrame:

    with open(json_file, 'r') as f:
        document = json.load(f)

    assert document['generator']

    elements = document['elements']

    assert len(elements) > 0

    # squish center points from Ways down to lat/lon like Points, and discard the center.
    for elem in elements:
        if 'center' in elem:
            elem['lat'] = elem['center']['lat']
            elem['lon'] = elem['center']['lon']
            del elem['center']
            del elem['nodes']

    df = pd.DataFrame(elements)

    for column in ('lat', 'lon'):
        df[f'{column}_rad'] = np.deg2rad(df[column].values)
        
    return df


def load_elements_from_json_file(filename: str) -> List:
    with open(filename, 'r') as f:
        document = json.load(f)

        assert document['generator']

        elements = document['elements']

        assert len(elements) > 0

        # squish center points from Ways down to lat/lon like Points, and discard the center.
        for elem in elements:
            if 'center' in elem:
                elem['lat'] = elem['center']['lat']
                elem['lon'] = elem['center']['lon']
                del elem['center']
                del elem['nodes']
        return elements


def find_closest_in_collection(query_df: pd.DataFrame, bicycle_parking_for_tree: pd.DataFrame, labeled="_closest") -> pd.DataFrame:

    # Ball Tree is a specialized version of a K-D tree that works in radians.
    search_ball = BallTree(bicycle_parking_for_tree[["lat_rad", "lon_rad"]].values, metric="haversine")

    # k results to find
    k = 1
    
    # vectorized work:
    #   - for each query, find the closest item in the Ball Tree,
    #          and emit its distance (unit-sphere) and index in the Ball Tree's original dataset (bicycle_parking_for_tree)
    distances, indicies = search_ball.query(query_df[["lat_rad", "lon_rad"]].values, k=k)

    # indicies is a vector of integer indexes with the same length as the query terms above.
    # Each index identifies a row in the bicycle_parking_for_tree dataframe.
    # We'll merge the two dataframes on this index later.
    # Store the vector with the original search query.
    query_df['index_of' + labeled] = indicies
    
    # distances is a vector of float values with the same length as the query terms above.
    # Each distance float was produced assuming the planet is a unit sphere.
    # Scale each distance to meters, and store the vector with the original search query.
    query_df[f'distance_meters' + labeled] = (lambda d: d * EARTH_RADIUS_KM * 1000)(distances).round()

    result_df = pd.merge(
        left=query_df, right=bicycle_parking_for_tree,
        left_on = 'index_of' + labeled, right_index=True,
        suffixes=('', labeled),
        validate='many_to_one'
    )

    # drop extra information about the right side
    del result_df['lat_rad' + labeled]
    del result_df['lon_rad' + labeled]
    del result_df['index_of' + labeled]
    del result_df['tags' + labeled]

    return result_df


def df_to_geojson(df: pd.DataFrame, lat='lat', lon='lon') -> FeatureCollection:
    features = df.apply(
        # this lambda function accepts a row from the dataframe,
        # and produces a Feature.
        lambda row: Feature(
            # geojson coordinates are reversed (lon/lat) compared to everything else here (lat/lon)
            geometry=Point((row[lon], row[lat])),
            properties=dict(row['tags'], **{
                "id": row["id"],
                "type": row["type"],
                "_id_closest": row["id_closest"],
                "_type_closest": row["type_closest"],
                "_lat_closest": row["lat_closest"],
                "_lon_closest": row["lon_closest"],
                "_distance_meters": row["distance_meters_closest"],
                "_under_one_minute": 1 if row["distance_meters_closest"] < 80 else 0, # 1 minute == 80 metres
                "_under_two_minute": 1 if row["distance_meters_closest"] < 160 else 0,  # 2 minute == 160 metres
                })
        ),
        axis=1,
    ).to_list()
    
    return FeatureCollection(features=features)


def df_to_geojson_with_catchment_lines(df: pd.DataFrame, lat='lat', lon='lon') -> FeatureCollection:
    features = df.apply(
        # this lambda function accepts a row from the dataframe,
        # and produces a Feature.
        lambda row: Feature(
            # geojson coordinates are reversed (lon/lat) compared to everything else here (lat/lon)
            geometry=LineString([(row[lon], row[lat]), (row["lon_closest"], row["lat_closest"])]),
            properties=dict(row['tags'], **{
                "id": row["id"],
                "type": row["type"],
                "_id_closest": row["id_closest"],
                "_type_closest": row["type_closest"],
                "_lat_closest": row["lat_closest"],
                "_lon_closest": row["lon_closest"],
                "_distance_meters": row["distance_meters_closest"],
                "_under_one_minute": 1 if row["distance_meters_closest"] < 80 else 0, # 1 minute == 80 metres
                "_under_two_minute": 1 if row["distance_meters_closest"] < 160 else 0,  # 2 minute == 160 metres
                })
        ),
        axis=1,
    ).to_list()
    
    return FeatureCollection(features=features)


def df_to_geojso_with_disparity(df: pd.DataFrame, disparity_column_suffix: str, lat='lat', lon='lon') -> FeatureCollection:
    features = df.apply(
        # this lambda function accepts a row from the dataframe,
        # and produces a Feature.
        lambda row: Feature(
            # geojson coordinates are reversed (lon/lat) compared to everything else here (lat/lon)
            geometry=Point((row[lon], row[lat])),
            properties=dict(row['tags'], **{
                "id": row["id"],
                "type": row["type"],
                "_id_closest": row["id_closest"],
                "_type_closest": row["type_closest"],
                "_lat_closest": row["lat_closest"],
                "_lon_closest": row["lon_closest"],
                "_distance_meters": row["distance_meters_closest"],
                "_distance_meters_disparity": row["distance_meters" + disparity_column_suffix],
                "_difference_distance_disparity": row["distance_meters" + disparity_column_suffix] - row["distance_meters_closest"],
                "_under_one_minute": 1 if row["distance_meters_closest"] < 80 else 0, # 1 minute == 80 metres
                "_under_two_minute": 1 if row["distance_meters_closest"] < 160 else 0,  # 2 minute == 160 metres
                })
        ),
        axis=1,
    ).to_list()
    
    return FeatureCollection(features=features)


def main():
    from argparse import ArgumentParser, Namespace

    p = ArgumentParser(description="For each element in $amenities, find the closest $parking")
    p.add_argument("--amenities", type=Path, metavar="shops.json", required=True)
    p.add_argument("--parking", type=Path, metavar="bicycle-parking.json", required=True)
    p.add_argument("--output", type=Path, metavar="output.geojson", required=True)
    p.add_argument("--catchment-lines", action="store_true")
    p.add_argument("--disparity-with", type=Path, metavar="car-parking,json")
    a: Namespace = p.parse_args()

    amenities_df = df_from_osm_json_file(a.amenities)
    search_space_for_tree_df = df_from_osm_json_file(a.parking)

    if len(search_space_for_tree_df) == 0:
        p.error("Parking list is empty, impossible to find closest.")

    print(f"Finding distance from {len(amenities_df)} features to nearest of {len(search_space_for_tree_df)} parking locations")

    results_df = find_closest_in_collection(amenities_df, search_space_for_tree_df)


    if a.disparity_with:
        disparity_df = df_from_osm_json_file(a.disparity_with)
        print(f"Finding distance from {len(amenities_df)} features to nearest of {len(disparity_df)} disparity locations")
        difference_df = find_closest_in_collection(results_df, disparity_df, labeled="_disparity")
        output_collection = df_to_geojso_with_disparity(difference_df, disparity_column_suffix="_disparity")

    elif a.catchment_lines:
        output_collection = df_to_geojson_with_catchment_lines(results_df)
    else:
        output_collection = df_to_geojson(results_df)
    
    with open(a.output, 'w') as f:
        json.dump(output_collection, f, indent=2)

    print(f"Wrote {len(output_collection['features'])} features")


if __name__ == "__main__":
    main()
