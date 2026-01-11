[out:json][timeout:300];
area[admin_level=8]["name"="Burlington"]["place"="city"]->.boundaryarea;
(
nw(area.boundaryarea)[amenity=bicycle_parking];
);
out center;
