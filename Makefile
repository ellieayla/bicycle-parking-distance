

# api call
downloads/bicycle-parking.json: overpass-queries/bicycle-parking.overpassql
	cat overpass-queries/bicycle-parking.overpassql | ./fetch-osm.sh > downloads/bicycle-parking.json

downloads/car-parking.json: overpass-queries/car-parking.overpassql
	cat overpass-queries/car-parking.overpassql | ./fetch-osm.sh > downloads/car-parking.json

downloads/shops.json: overpass-queries/shops.overpassql
	cat overpass-queries/shops.overpassql | ./fetch-osm.sh > downloads/shops.json

downloads/buildings.json: overpass-queries/buildings.overpassql
	cat overpass-queries/buildings.overpassql | ./fetch-osm.sh > downloads/buildings.json


.PHONY: download
download: downloads/bicycle-parking.json downloads/car-parking.json downloads/shops.json downloads/buildings.json
	ls -l downloads/

.PHONY: clean
clean:
	rm -fv bicycle-parking.json car-parking.json shops.json




