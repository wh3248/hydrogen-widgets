"""
    location_map.py
"""
import os
from typing import List
import shapefile
import pandas as pd
import plotly.graph_objects as go
from hydrogen_common import get_domain_path, get_domain_state
from hydrogen_widgets.utilities.create_plotly_html_file import create_plotly_html_file

# pylint: disable=C0103,R0914


def render_location_map(user_id:str, domain_id:str)->dict:
    """
    Return the data to render the data for the location map widget.


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
        domain_bounds = domain_state["wgs84_bounds"]

        # The aspect ratio of the USA map is 0.5
        aspectRatio = 0.5

        ## load in watershed outline
        shapefile_path = f"{domain_path}/domain_files/domain.shp"
        watershed = shapefile.Reader(shapefile_path)

        # read points from the watershed shapefile
        shapefile_points = []
        for shape in watershed.shapes():
            for i in shape.points:
                shapefile_points.append(i)

        shapefile_points = pd.DataFrame(shapefile_points, columns=["lon", "lat"])

        # load observation locations
        obs_site_file = f"{domain_path}/domain_files/obs_sites.csv"
        OBS = pd.read_csv(obs_site_file)

        ### panel 2: geographic location and data points
        bbox_lat = (
            domain_bounds[1],
            domain_bounds[1],
            domain_bounds[3],
            domain_bounds[3],
            domain_bounds[1],
        )
        bbox_lon = (
            domain_bounds[0],
            domain_bounds[2],
            domain_bounds[2],
            domain_bounds[0],
            domain_bounds[0],
        )

        observation_points = go.Scattergeo(
            lon=OBS["longitude"], lat=OBS["latitude"], name="Observations"
        )

        watershed_bounderies = go.Scattergeo(
            lon=shapefile_points["lon"],
            lat=shapefile_points["lat"],
            mode="lines",
            name="Watershed",
            line=dict(width=1, color="cyan"),
        )

        traces = []
        traces.append(
            {
                "type": "scattergeo",
                "lat": bbox_lat,
                "lon": bbox_lon,
                "mode": "lines",
                "name": "Bounding Box",
                "line": {"width": 1, "color": "black"},
            }
        )

        traces.append(
            {
                "type": "scattergeo",
                "lat": observation_points["lat"].tolist(),
                "lon": observation_points["lon"].tolist(),
                "mode": "markers",
                "marker": {"size": 3, "color": "blue"},
            }
        )

        traces.append(
            {
                "type": "scattergeo",
                "lat": watershed_bounderies["lat"].tolist(),
                "lon": watershed_bounderies["lon"].tolist(),
                "mode": "lines",
                "line": {"width": 1, "color": "cyan"},
            }
        )

        projection_scale = get_projection_scale(domain_bounds)

        layout = {
            "margin": {"r": 0, "t": 0, "b": 0, "l": 0},
            "geo": {
                "scope": "usa",
                "projection": {"scale": projection_scale},
                "showcoastlines": True,
                "coastlinecolor": "RebeccaPurple",
                "showland": True,
                "landcolor": "LightBlue",
                "showocean": True,
                "oceancolor": "LightBlue",
                "showlakes": True,
                "lakecolor": "Blue",
                "center": {
                    "lat": (bbox_lat[0] + bbox_lat[2]) / 2,
                    "lon": (bbox_lon[0] + bbox_lon[1]) / 2,
                },
            },
            "showlegend": False,
        }

        response = {"aspectRatio": round(aspectRatio,2), "traces": traces, "layout": layout}
        return response
    except Exception as e:
        raise Exception(
            f"Unable to render data for location map because {str(e)}"
        ) from e


def get_projection_scale(domain_bounds:List[int])->int:
    """Compute the default projection scale given the domain bounds"""

    if len(domain_bounds) == 4:
        lon_size = domain_bounds[2] - domain_bounds[0]
        lat_size = domain_bounds[3] - domain_bounds[1]
        if lon_size < 0.6 and lat_size < 0.25:
            result = 55
        elif lon_size < 1.0 and lat_size < 0.6:
            result = 30
        elif lon_size < 1.8 and lat_size < 1.5:
            result = 10
        else:
            result = 5
    else:
        result = 55
    return result

if __name__ == "__main__":
    # Generate local HTML file for local testing

    # Set env variable to root of simulated user domain root directory
    os.environ["CLIENT_HYDRO_DATA_PATH"] = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tests/test_data")
    )
    # Generate widget result for a user domain in the simulated root directory
    api_result = render_location_map("test_user", "test_domain")

    # Generate HTML and javascript to view widget result locally
    create_plotly_html_file(__file__, api_result)
