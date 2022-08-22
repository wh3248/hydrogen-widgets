"""
    Terrain Map Widget
"""
import os
import datetime
import logging
from typing import List
import shapefile
import pandas
import xarray
from hydrogen_common import get_domain_path, get_domain_state
from hydrogen_widgets.utilities.create_plotly_html_file import create_plotly_html_file

# pylint: disable=C0200,R0914,C0103


def render_terrain_map(user_id:str, domain_id:str)->dict:
    """
    Return the data to render a terrain map widget.

    Parameters
    ----------
    user_id: str
        User id of the domain to get data.
    domain_id: str
        Domain id that identifies the user domain containing the widget data.

    Returns
    -------
    dict
        A dictionary (json structure) containing the response to be sent back to the UI
    """

    try:
        domain_path = get_domain_path(user_id=user_id, domain_directory=domain_id)
        domain_state = get_domain_state(user_id=user_id, domain_directory=domain_id)
        wgs84_bounds = domain_state.get("wgs84_bounds", None)
        shape_file_path = get_shape_file_path(domain_path)
        response = get_watershed_and_gauge_info(
            domain_path, shape_file_path, wgs84_bounds
        )
        return response
    except Exception as e:
        raise Exception("Unable to render terrain map") from e


def get_shape_file_path(domain_path:str)->str:
    """Get path name to the shapefile of the domain."""

    shape_file_path = None
    domain_files_path = f"{domain_path}/domain_files"
    if os.path.exists(domain_files_path):
        for file in os.listdir(domain_files_path):
            if file.endswith(".shp"):
                shape_file_path = f"{domain_files_path}/" + file
                break
    if shape_file_path is None:
        raise Exception("Shapefile of domain not found.")
    return shape_file_path


def get_watershed_and_gauge_info(domain_path:str, shape_file_path:str, wgs84_bounds:List[int])->dict:
    """
    Compute latitude/longitude points for each huc within the shapefile and return plotly traces and layout
    to render a terrain map with the bounding box, huc boundaries and observation points.
    """

    if not os.path.exists(shape_file_path):
        raise Exception(f"Shape file {shape_file_path} does not exist.")

    watershed = shapefile.Reader(shape_file_path)
    huc_info_list = []
    min_lon = 1000
    max_lon = -1000
    min_lat = 1000
    max_lat = -1000

    for shape in watershed.shapes():
        lon_points = []
        lat_points = []
        for point in shape.points:
            lon = point[0]
            lat = point[1]
            max_lon = lon if lon > max_lon else max_lon
            min_lon = lon if lon < min_lon else min_lon
            max_lat = lat if lat > max_lat else max_lat
            min_lat = lat if lat < min_lat else min_lat
            lon_points.append(str(lon))
            lat_points.append(str(lat))

        center_lon = (max_lon + min_lon) / 2
        center_lat = (max_lat + min_lat) / 2

        # creates the huc object and adds it to the list, for each huc
        huc_info = {
            "lat": lat_points,
            "lon": lon_points,
        }
        huc_info_list.append(huc_info)

    gauge_labels_in_shapefile = get_observation_sites(domain_path)

    traces = []


    # Add HUC boundary lines
    for region in huc_info_list:
        traces.append(
            {
                "name": "Watershed",
                "type": "scattermapbox",
                "lon": region.get("lon"),
                "lat": region.get("lat"),
                "mode": "lines",
                "line": {"width": 2, "color": "cyan", "size": 4},
            }
        )

    # Add stream flow markers
    add_observation_type_makers(traces, gauge_labels_in_shapefile, "streamflow", "Stream", "blue")
    add_observation_type_makers(traces, gauge_labels_in_shapefile, "groundwater", "Well", "lightblue")

    # Add bounding box lines
    traces.append(
        {
            "name": "Bounding box",
            "type": "scattermapbox",
            "lon": [
                wgs84_bounds[0],
                wgs84_bounds[0],
                wgs84_bounds[2],
                wgs84_bounds[2],
                wgs84_bounds[0],
            ],
            "lat": [
                wgs84_bounds[1],
                wgs84_bounds[3],
                wgs84_bounds[3],
                wgs84_bounds[1],
                wgs84_bounds[1],
            ],
            "mode": "lines",
            "line": {"width": 1, "color": "black", "size": 1},
        }
    )

    zoom_level = get_zoom_level(wgs84_bounds)

    # Define plotly layout
    layout = {
        "dragmode": "zoom",
        "mapbox": {
            "style": "white-bg",
            "layers": [
                {
                    "sourcetype": "raster",
                    "source": [
                        "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                    ],
                    "below": "traces",
                }
            ],
            "center": {"lat": center_lat, "lon": center_lon},
            "zoom": zoom_level,
        },
        "showlegend": False,
        "margin": {"r": 25, "t": 30, "b": 0, "l": 0},
    }

    # return response
    response = {
        "traces": traces,
        "layout": layout,
        "click_marker": {
            "global_state": "terrainSite",
            "state_values": {
                "site_type": "site_types[]",
                "site_name": "site_names[]",
                "site_id": "site_ids[]"
            }
        }
    }
    return response

def get_zoom_level(wgs84_bounds):
    """Get the default zoom level given the lat/lon bounds"""
    if len(wgs84_bounds) == 4:
        lon_size = wgs84_bounds[2] - wgs84_bounds[0]
        lat_size = wgs84_bounds[3] - wgs84_bounds[1]
        if lon_size < 0.6 and lat_size < 0.25:
            result = 9
        elif lon_size < 1.0 and lat_size < 0.6:
            result = 7
        elif lon_size < 1.8 and lat_size < 1.5:
            result = 6
        else:
            result = 5
    else:
        result = 9
    return result

def add_observation_type_makers(traces, labels_in_shapefile, obs_type, obs_type_name, marker_color):
    """Add stream flow or groundwater markers traces."""

    lats = []
    lons = []
    texts = []
    site_ids = []
    site_names = []
    site_types = []
    for label in labels_in_shapefile:
        site_type = label.get("site_type", "")
        if site_type == obs_type:
            lat = label.get("lat")
            lon = label.get("lon")
            site_id = label.get("site_id", "")
            site_name = label.get("site_name", "")
            lats.append(lat)
            lons.append(lon)
            texts.append(f"{site_name}")
            site_ids.append(site_id)
            site_names.append(site_name)
            site_types.append(site_type)

    if len(lats) > 0:
        traces.append(
            {
                "name": obs_type_name,
                "type":"scattermapbox",
                "lon": lons,
                "lat": lats,
                "text": texts,
                "site_ids": site_ids,
                "site_names": site_names,
                "site_types": site_types,
                "mode": 'markers',
                "marker" : {
                    "size":10,
                    "color": marker_color
                }
            }
        )

def render_streamflow_graph(message):
    """Deprecated. Not used. Execute the job using the arguments in the json message: site_id."""

    try:
        domain_path = get_domain_path(message)
        query_parameters = message.get("query_parameters", {})
        site_id = query_parameters.get("site_id", None)
        if site_id is None:
            raise Exception("No site_id provided.")
        response = get_streamflow_data(domain_path, site_id)
        return response
    except Exception as e:
        raise Exception("Unable to render terrain map") from e


def get_streamflow_data(domain_path, site_id):
    """Deprecated. Not used. Get the stream flow data for the stream flow from the domain observations"""

    filepath = f"{domain_path}/observations/streamflow/"
    streamflow_filepath = filepath + site_id + ".nc"
    logging.info("Read streamflow data from '%s'", streamflow_filepath)
    streamflow = xarray.open_dataset(streamflow_filepath)
    streamflow = streamflow.dropna(dim="datetime")
    streamflow["datetime"] = pandas.DatetimeIndex(streamflow["datetime"].values)
    number_of_date_points = streamflow.streamflow.shape[0]
    if number_of_date_points > 0:
        first_date = datetime.date.fromtimestamp(
            int(streamflow.datetime[0]) / 1000000000
        ).strftime("%Y-%m-%d")
        last_date = datetime.date.fromtimestamp(
            int(streamflow.datetime[number_of_date_points - 1]) / 1000000000
        ).strftime("%Y-%m-%d")
    else:
        first_date = None
        last_date = None

    # limit the number of months of data returned, but return enough ...
    range_max = datetime.datetime.today().date()
    range_min = range_max - pandas.DateOffset(months=12 * 15)

    # select data from original ds with dates in that range (through present)
    streamflow_past_six_months = streamflow.sel(
        datetime=streamflow.datetime >= range_min
    )

    dates = streamflow_past_six_months["datetime"]
    streamflow = streamflow_past_six_months["streamflow"]

    dates = dates.to_numpy().tolist()
    streamflow = streamflow.to_numpy().tolist()

    for date in range(len(dates)):
        dates[date] = datetime.date.fromtimestamp(int(dates[date] / 1000000000))
        dates[date] = dates[date].strftime("%Y-%m-%d")

    streamflow_time = {
        "x_points": dates,
        "y_points": streamflow,
        "points_in_file": number_of_date_points,
        "first_date": first_date,
        "last_date": last_date,
    }

    return streamflow_time


def get_observation_sites(domain_path):
    """Get the streamflow and groundwater depth gauges for the domain using the obs_sites.csv domain file."""

    result = []
    gauge_site_file_path = f"{domain_path}/domain_files/obs_sites.csv"
    if os.path.exists(gauge_site_file_path):
        with open(gauge_site_file_path, "r") as stream:
            n = 0
            contents = stream.read()
            rows = contents.split("\n")
            for line in rows:
                if n > 0:
                    columns = line.split(",")
                    if len(columns) >= 7:
                        gauge_label = {
                            "site_type": columns[0],
                            "lat": columns[3],
                            "lon": columns[4],
                            "site_id": columns[1],
                            "site_name": columns[2],
                            "start_date": columns[6],
                            "end_date": columns[7],
                        }
                        result.append(gauge_label)
                n = n + 1
    return result


if __name__ == "__main__":
    # Generate local HTML file for local testing

    # Set env variable to root of simulated user domain root directory
    os.environ["CLIENT_HYDRO_DATA_PATH"] = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tests/test_data")
    )
    # Generate widget result for a user domain in the simulated root directory
    api_result = render_terrain_map("test_user", "test_domain")

    # Generate HTML and javascript to view widget result locally
    create_plotly_html_file(__file__, api_result)
