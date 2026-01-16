#!/bin/sh

# usage: cat overpass-query.ql | ./fetch-osm.sh > osm-data.json
curl --fail --retry 8 --retry-delay 30 -v -d @- -X POST http://overpass-api.de/api/interpreter
