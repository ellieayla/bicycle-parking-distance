[out:json][timeout:300];
area[admin_level=8]["name"="Burlington"]["place"="city"]->.boundaryarea;
(
nw(area.boundaryarea)[amenity][amenity!=bicycle_parking][amenity!=parking_space][amenity!=parking][amenity!=parking_entrance][amenity!=bench][amenity!=waste_basket][amenity!=post_box];
nw(area.boundaryarea)[shop];
nw(area.boundaryarea)[leisure][access!=private];
nw(area.boundaryarea)[tourism][tourism!=artwork][information!=map][access!=private];
node(area.boundaryarea)[public_transport=station];
);
out center;
