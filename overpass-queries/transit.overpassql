[out:json][timeout:300];
area[admin_level=8]["name"="Burlington"]["place"="city"]->.boundaryarea;
(
node(area.boundaryarea)[public_transport];
nw(area.boundaryarea)[highway=bus_stop];
);
out center;
