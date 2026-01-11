from typing import Any, List, Dict, TypedDict, NamedTuple, Tuple, Optional
import json
from pathlib import Path
from geopy.distance import geodesic, Distance
import sys
from geojson import Feature, Point, FeatureCollection
from progress.bar import Bar

def load_elements_from_json_file(filename: str) -> List:
    with open(filename, 'r') as f:
        document = json.load(f)

        assert document['generator']

        elements = document['elements']

        assert len(elements) > 0
        return elements



def get_lat_lon_from_osm_nwr(nwr: dict) -> Tuple[float, float]:
    try:
        return nwr['lat'], nwr['lon']
    except KeyError:
        return nwr['center']['lat'], nwr['center']['lon']


def find_closest_in_collection(node_of_interest, collection_of_nodes: List[dict]) -> Tuple[dict[str, Any], Distance]:
    closest_from_collection: Optional[dict[str, Any]] = None
    closest_distance: Optional[Distance] = None

    node_of_interest_lat_lon = get_lat_lon_from_osm_nwr(node_of_interest)

    for n in collection_of_nodes:

        # inputs to geodesic are (lat, long) tuples
        possible_closest_lat_lon = get_lat_lon_from_osm_nwr(n)
        
        distance = geodesic(node_of_interest_lat_lon, possible_closest_lat_lon )

        if closest_distance is None or closest_distance > distance:
            closest_distance = distance
            closest_from_collection = n

    if closest_distance is None or closest_from_collection is None:
        raise ValueError("Unable to find any distance to item in source collection.")

    return (closest_from_collection, closest_distance)


def create_feature_about_subject(node_of_interest: dict, distance: Distance, closest_item: dict) -> Feature:
        # Make a Feature about the /node of interest/

    """
    { "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [ -151.5129, 63.1016, 0.0 ] }
      "properties": { "id": "ak16994521", "mag": 2.3, "time": 1507425650893, "felt": null, "tsunami": 0 },
    },
    """

    # https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.1
    # The first two elements are longitude and latitude, ...  precisely in that order and using decimal numbers.
    # That's reversed from input data.
    lat, lon = get_lat_lon_from_osm_nwr(node_of_interest)
    location = Point((lon, lat))

    properties: dict = node_of_interest['tags'].copy()
    properties['id'] = node_of_interest['id']
    properties['type'] = node_of_interest['type']

    properties["_distance_km"] = distance.km,
    properties["_under_one_minute"] = distance.km < 0.080, # 1 minute == 80 metres
    properties["_under_two_minute"] = distance.km < (2 * 0.080), # 2 minute == 160 metres
    
    properties['_closest'] = {
        "id": closest_item['id'],
        "type": closest_item['type'],
    }

    return Feature(
        geometry=location,
        properties=properties
    )


def main():
    from argparse import ArgumentParser, Namespace, FileType

    p = ArgumentParser(description="For each element in $amenities, find the closest $parking")
    p.add_argument("--amenities", type=Path, metavar="shops.json", required=True)
    p.add_argument("--parking", type=Path, metavar="bicycle-parking.json", required=True)
    p.add_argument("--output", type=Path, metavar="output.geojson", default=sys.stdout)
    
    a: Namespace = p.parse_args()

    amenities = load_elements_from_json_file(a.amenities)
    bicycle_parking = load_elements_from_json_file(a.parking)

    if len(bicycle_parking) == 0:
        p.error("Parking list is empty, impossible to find closest.")

    with Bar(max=len(amenities)) as progress_bar:
        output_features = []
        for input_feature in amenities:
            closest_item, distance = find_closest_in_collection(input_feature, bicycle_parking)
            annotated_feature_for_heatmap = create_feature_about_subject(input_feature, distance, closest_item)
            output_features.append(annotated_feature_for_heatmap)
            progress_bar.next()
        
        output_collection = FeatureCollection(output_features)

    if a.output is sys.stdout:
        json.dumps(output_collection, indent=2)
    else:
        with open(a.output, 'w') as f:
            json.dump(output_collection, f, indent=2)


if __name__ == "__main__":
    main()
