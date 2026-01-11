[out:json][timeout:300];
area[admin_level=8]["name"="Burlington"]["place"="city"]->.boundaryarea;
(
nw(area.boundaryarea)[amenity][amenity!=bicycle_parking][amenity!=parking_space][amenity!=parking][amenity!=parking_entrance];
nw(area.boundaryarea)[shop];
node(area.boundaryarea)[public_transport];
nw(area.boundaryarea)[highway=bus_stop];
);
out center;
