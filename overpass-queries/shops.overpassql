[out:json][timeout:300];
area[admin_level=8]["name"="Burlington"]["place"="city"]->.boundaryarea;
(
nw(area.boundaryarea)[amenity][amenity!=bicycle_parking][amenity!=parking_space][amenity!=parking][amenity!=parking_entrance][amenity!=bench][amenity!=waste_basket];
nw(area.boundaryarea)[shop];
nw(area.boundaryarea)[leisure][access!=private];
node(area.boundaryarea)[public_transport=station];
);
out center;
