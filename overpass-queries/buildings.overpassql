[out:json][timeout:300];
area[admin_level=8]["name"="Burlington"]["place"="city"]->.boundaryarea;
(
way(area.boundaryarea)[building];
);
out center;
