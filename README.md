What's the nearest bicycle parking location for a given shop?
Are there cafes which don't have any parking nearby?
Is there a bike-rack-desert in the city?

Export lists of shops and bike parking locations from OSM, compute N*M distances, finding the closest for each shop.

Emit a geojson file for each shop annotated with the distance to the nearest bike parking location.

This can be further processed similar to https://overpass-ultra.us/docs/MapLibre-Examples/heatmap-layer/


By default, processes OSM data for Burlington Ontario, and commits results back to repository, can be cited using github raw urls:

* [Distance from shops to nearest bicycle parking](distance_from_shops_to_nearest_bicycle_parking.geojson)
* [Distance from every _building_ to nearest bicycle parking](distance_from_buildings_to_nearest_bicycle_parking.geojson)

and for comparison, the carparks;

* [Distance from shops to nearest car parking](distance_from_shops_to_nearest_car-parking.geojson)
* [Distance from every building to nearest car parking](distance_from_buildings_to_nearest_car-parking.geojson)
