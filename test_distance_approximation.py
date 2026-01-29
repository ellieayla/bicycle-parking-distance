import numpy as np
import pandas as pd
from geojson import Feature, FeatureCollection, dumps
from main import df_to_geojson


def test_dataframe_to_geojson_feature_collection() -> None:

    merge_result_dict = {'type': {0: 'way', 1: 'way', 2: 'way', 3: 'way'}, 'id': {0: 13960135, 1: 24835556, 2: 25338806, 3: 25464956}, 'tags': {0: {'addr:city': 'Burlington', 'addr:housenumber': '777', 'addr:street': 'Guelph Line', 'building': 'retail', 'building:levels': '1', 'name': 'Burlington Centre', 'opening_hours': 'Mo-Fr 10:00-21:00; Sa 09:30-18:00; Su 12:00-17:00', 'shop': 'mall', 'smoking': 'outside', 'wikidata': 'Q4999257', 'wikipedia': 'en:Burlington Centre'}, 1: {'addr:city': 'Burlington', 'addr:housenumber': '867', 'addr:postcode': 'L7S 1A1', 'addr:province': 'ON', 'addr:street': 'Lakeshore Road', 'building': 'yes', 'building:levels': '7', 'government': 'public_service', 'name': 'Canada Centre for Inland Waters', 'office': 'research', 'operator': 'Environment and Climate Change Canada', 'website': 'https://profils-profiles.science.gc.ca/en/research-centre/canada-centre-inland-waters'}, 2: {'addr:housenumber': '2025', 'addr:street': 'Guelph Line', 'building': 'retail', 'building:levels': '1', 'roof:levels': '0', 'toilets': 'yes', 'toilets:wheelchair': 'yes', 'wheelchair': 'yes'}, 3: {'building': 'block', 'name': 'AIC'}}, 'lat': {0: 43.3483465, 1: 43.2989701, 2: 43.3666377, 3: 43.3412267}, 'lon': {0: -79.7935195, 1: -79.8006915, 2: -79.8222113, 3: -79.8339227}, 'distance_meters': {0: 132.85147549600796, 1: 81.44035331775225, 2: 53.52223280841795, 3: 191.8336399157924}, 'type_closest': {0: 'way', 1: 'way', 2: 'node', 3: 'way'}, 'id_closest': {0: 154904418, 1: 442230811, 2: 12663529968, 3: 186353929}, 'lat_closest': {0: 43.3494614, 1: 43.2991818, 2: 43.3663466, 3: 43.3428995}, 'lon_closest': {0: -79.7941101, 1: -79.7997281, 2: -79.821684, 3: -79.8333425}}

    # results of processing full dataset have this shape
    merge_result = pd.DataFrame.from_dict(merge_result_dict)
    print(merge_result)

    # SUT
    feature_collection: FeatureCollection = df_to_geojson(merge_result)

    # verify
    assert len(feature_collection['features']) == 4

    for feature in feature_collection['features']:
        assert isinstance(feature, Feature)
        assert 10 < feature["properties"]["_distance_meters"] < 200  # everything is nearby
        assert feature["properties"]['_under_one_minute'] in (0, 1)

        assert -79.9 < feature["geometry"]["coordinates"][0] < -79.4  # source data longitudes are all in this range

    # can be serialized
    _ = dumps(feature_collection, indent=2)


def test_ball_tree_plan() -> None:
    from main import find_closest_in_collection

    query_df = pd.DataFrame.from_dict(
        {'type': {0: 'way'}, 'id': {0: 13960135}, 'tags': {0: {'addr:city': 'Burlington', 'addr:housenumber': '777', 'addr:street': 'Guelph Line', 'building': 'retail', 'building:levels': '1', 'name': 'Burlington Centre', 'opening_hours': 'Mo-Fr 10:00-21:00; Sa 09:30-18:00; Su 12:00-17:00', 'shop': 'mall', 'smoking': 'outside', 'wikidata': 'Q4999257', 'wikipedia': 'en:Burlington Centre'}}, 'lat': {0: 43.3483465}, 'lon': {0: -79.7935195},}
    )
    for column in ('lat', 'lon'):
        query_df[f'{column}_rad'] = np.deg2rad(query_df[column].values)

    bicycle_parking_for_tree = pd.DataFrame.from_dict(
        {'type': {0: 'node', 1: 'node', 2: 'way', 3: 'node'}, 'id': {0: 1356846891, 1: 1615155957, 2: 1423550542, 3: 11615021109}, 'lat': {0: 43.3133162, 1: 43.3871208, 2: 43.3133067, 3: 43.3470884}, 'lon': {0: -79.8534052, 1: -79.8116887, 2: -79.8533965, 3: -79.7940899}, 'tags': {0: {'amenity': 'bicycle_parking', 'bicycle_parking': 'rack', 'capacity': '16', 'covered': 'yes', 'operator': 'GO Transit'}, 1: {'amenity': 'bicycle_parking'}, 2: {'access': 'yes', 'amenity': 'bicycle_parking', 'bicycle_parking': 'shed', 'building': 'shed', 'capacity': '16', 'covered': 'yes', 'fee': 'no'}, 3: {'amenity': 'bicycle_parking', 'loc': 'mall_edge'}}, }
    )

    for column in ('lat', 'lon'):
        bicycle_parking_for_tree[f'{column}_rad'] = np.deg2rad(bicycle_parking_for_tree[column].values)

    result = find_closest_in_collection(query_df, bicycle_parking_for_tree)
    print(result)

    assert len(result) == 1

    r: pd.DataFrame = result[['id_closest']]
    assert r.to_dict() == {'id_closest': {0: 11615021109}}  # a rack right outside the mall
