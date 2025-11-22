# Environment value export script
# shp
export PATH_COUNTRIES="./data/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp"
export PATH_DISPUTED="./data/ne_50m_admin_0_breakaway_disputed_areas/ne_50m_admin_0_breakaway_disputed_areas.shp"
export PATH_LAKES="./data/ne_50m_lakes/ne_50m_lakes.shp"
export PATH_RIVERS="./data/ne_50m_rivers_lake_centerlines/ne_50m_rivers_lake_centerlines.shp"
export PATH_RASTER="./data/NE1_50M_SR_W/NE1_50M_SR_W.tif"

# execute uv run
uv run main.py
