[out:json][timeout:300];
area[admin_level=8]["name"="Burlington"]["place"="city"]->.boundaryarea;
(
nw(area.boundaryarea)[amenity=parking];
nw(area.boundaryarea)[amenity=parking_space];
);
out center;
